import json
import logging

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from app.services.speech_service import speech_service

router = APIRouter()
logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
CHUNK_SECONDS = 4
CHUNK_SIZE = SAMPLE_RATE * CHUNK_SECONDS


async def process_audio(websocket: WebSocket, audio: np.ndarray):
    if audio.size == 0:
        logger.warning("Received empty audio buffer")
        return

    duration = len(audio) / SAMPLE_RATE

    logger.info(
        "Starting transcription: %.2f seconds of audio, %d samples",
        duration,
        len(audio)
    )

    try:
        result = await run_in_threadpool(
            speech_service.transcribe_audio,
            audio
        )

        logger.info(
            "Transcription finished: text_length=%d, language=%s",
            len(result.get("text", "")),
            result.get("language", "unknown")
        )

        await websocket.send_json({
            "type": "transcription",
            "text": result["text"],
            "language": result["language"],
            "language_probability": result["language_probability"]
        })

    except Exception:
        logger.exception("Audio processing failed")

        await websocket.send_json({
            "type": "error",
            "message": "Unable to process audio. Please try again."
        })


@router.websocket("/ws/transcribe")
async def transcribe_stream(websocket: WebSocket):
    await websocket.accept()

    audio_buffer = np.array([], dtype=np.float32)
    total_bytes = 0
    chunk_count = 0

    logger.info("WebSocket connection established")

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                logger.info("Client disconnected")
                break

            if message.get("bytes") is not None:
                raw_audio = message["bytes"]

                if not raw_audio:
                    continue

                total_bytes += len(raw_audio)
                chunk_count += 1

                audio_chunk = np.frombuffer(
                    raw_audio,
                    dtype=np.float32
                )

                if audio_chunk.size == 0:
                    continue

                if not np.isfinite(audio_chunk).all():
                    logger.warning("Invalid audio data received")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid audio data received"
                    })
                    continue

                audio_buffer = np.concatenate(
                    [audio_buffer, audio_chunk]
                )

                if chunk_count % 50 == 0:
                    logger.info(
                        "Audio received: chunks=%d, bytes=%d, buffered_samples=%d",
                        chunk_count,
                        total_bytes,
                        len(audio_buffer)
                    )

                while len(audio_buffer) >= CHUNK_SIZE:
                    current_audio = audio_buffer[:CHUNK_SIZE]
                    audio_buffer = audio_buffer[CHUNK_SIZE:]

                    await process_audio(websocket, current_audio)

            elif message.get("text"):
                try:
                    command = json.loads(message["text"])
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON command received")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON command"
                    })
                    continue

                if command.get("action") == "stop":
                    logger.info(
                        "Stop command received: chunks=%d, bytes=%d, remaining_samples=%d",
                        chunk_count,
                        total_bytes,
                        len(audio_buffer)
                    )

                    if len(audio_buffer) > 0:
                        await process_audio(websocket, audio_buffer)
                        audio_buffer = np.array([], dtype=np.float32)

                    await websocket.send_json({
                        "type": "completed",
                        "message": "Transcription completed"
                    })

                    logger.info("Transcription completed successfully")
                    break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception:
        logger.exception("WebSocket transcription error")

        try:
            await websocket.send_json({
                "type": "error",
                "message": "Speech transcription failed"
            })
        except Exception:
            pass

    finally:
        try:
            await websocket.close()
        except Exception:
            pass

        logger.info("WebSocket connection closed")