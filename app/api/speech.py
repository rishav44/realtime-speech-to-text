
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
        logger.warning("Received empty audio")
        return

    logger.info(
        "Starting transcription: %.2f seconds of audio",
        len(audio) / SAMPLE_RATE
    )

    result = await run_in_threadpool(
        speech_service.transcribe_audio,
        audio
    )

    logger.info(
        "Transcription finished. Text length: %d, Language: %s",
        len(result["text"]),
        result["language"]
    )

    await websocket.send_json({
        "type": "transcription",
        "text": result["text"],
        "language": result["language"],
        "language_probability": result["language_probability"]
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
                total_bytes += len(raw_audio)

                audio_chunk = np.frombuffer(
                    raw_audio,
                    dtype=np.float32
                )

                if audio_chunk.size == 0:
                    continue

                if not np.isfinite(audio_chunk).all():
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid audio data received"
                    })
                    continue

                audio_buffer = np.concatenate(
                    [audio_buffer, audio_chunk]
                )

                while len(audio_buffer) >= CHUNK_SIZE:
                    current_audio = audio_buffer[:CHUNK_SIZE]
                    audio_buffer = audio_buffer[CHUNK_SIZE:]

                    chunk_count += 1
                    logger.info("Processing audio chunk %d", chunk_count)

                    await process_audio(websocket, current_audio)

            elif message.get("text"):
                try:
                    command = json.loads(message["text"])
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON command"
                    })
                    continue

                if command.get("action") == "stop":
                    logger.info(
                        "Stop received. Total audio bytes: %d, chunks: %d, remaining samples: %d",
                        total_bytes,
                        chunk_count,
                        len(audio_buffer)
                    )

                    if len(audio_buffer) > 0:
                        await process_audio(websocket, audio_buffer)

                    await websocket.send_json({
                        "type": "completed",
                        "message": "Transcription completed"
                    })

                    logger.info("Transcription completed successfully")
                    break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception:
        logger.exception("Speech WebSocket error")

        try:
            await websocket.send_json({
                "type": "error",
                "message": "Speech transcription failed. Check server logs."
            })
        except Exception:
            pass

    finally:
        try:
            await websocket.close()
        except Exception:
            pass

        logger.info("WebSocket connection closed")
