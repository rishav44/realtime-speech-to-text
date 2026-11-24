
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
        print("DEBUG: RECEIVED EMPTY AUDIO", flush=True)
        return

    duration = len(audio) / SAMPLE_RATE

    logger.info("Starting transcription: %.2f seconds", duration)
    print(
        f"DEBUG: STARTING TRANSCRIPTION - {duration:.2f} seconds",
        flush=True
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

    print(
        f"DEBUG: TRANSCRIPTION FINISHED - "
        f"Text length: {len(result['text'])}, "
        f"Language: {result['language']}",
        flush=True
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

    print("DEBUG: SPEECH WEBSOCKET ENDPOINT REACHED", flush=True)

    audio_buffer = np.array([], dtype=np.float32)
    total_bytes = 0
    chunk_count = 0

    logger.info("WebSocket connection established")
    print("DEBUG: WEBSOCKET CONNECTION ESTABLISHED", flush=True)

    try:
        while True:

            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                logger.info("Client disconnected")
                print("DEBUG: CLIENT DISCONNECTED", flush=True)
                break

            # Receive audio bytes from browser
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

                print(
                    f"DEBUG: AUDIO RECEIVED - "
                    f"{len(audio_chunk)} samples, "
                    f"Total bytes: {total_bytes}",
                    flush=True
                )

                # Process audio in 4-second chunks
                while len(audio_buffer) >= CHUNK_SIZE:

                    current_audio = audio_buffer[:CHUNK_SIZE]
                    audio_buffer = audio_buffer[CHUNK_SIZE:]

                    chunk_count += 1

                    logger.info(
                        "Processing audio chunk %d",
                        chunk_count
                    )

                    print(
                        f"DEBUG: PROCESSING AUDIO CHUNK {chunk_count}",
                        flush=True
                    )

                    await process_audio(
                        websocket,
                        current_audio
                    )

            # Receive stop command
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
                        "Stop received. Total audio bytes: %d, "
                        "chunks: %d, remaining samples: %d",
                        total_bytes,
                        chunk_count,
                        len(audio_buffer)
                    )

                    print(
                        f"DEBUG: STOP RECEIVED - "
                        f"Total bytes: {total_bytes}, "
                        f"Chunks: {chunk_count}, "
                        f"Remaining samples: {len(audio_buffer)}",
                        flush=True
                    )

                    # Process remaining audio
                    if len(audio_buffer) > 0:

                        await process_audio(
                            websocket,
                            audio_buffer
                        )

                    await websocket.send_json({
                        "type": "completed",
                        "message": "Transcription completed"
                    })

                    logger.info("Transcription completed successfully")

                    print(
                        "DEBUG: TRANSCRIPTION COMPLETED SUCCESSFULLY",
                        flush=True
                    )

                    break

    except WebSocketDisconnect:

        logger.info("WebSocket disconnected")
        print("DEBUG: WEBSOCKET DISCONNECTED", flush=True)

    except Exception as error:

        logger.exception("Speech WebSocket error: %s", error)

        print(
            f"DEBUG: WEBSOCKET ERROR - {error}",
            flush=True
        )

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
        print("DEBUG: WEBSOCKET CONNECTION CLOSED", flush=True)
