
import json
import logging

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from app.services.speech_service import speech_service


router = APIRouter()
logger = logging.getLogger(__name__)


# Audio configuration
SAMPLE_RATE = 16000
CHUNK_SECONDS = 4
CHUNK_SIZE = SAMPLE_RATE * CHUNK_SECONDS


async def process_audio(websocket: WebSocket, audio: np.ndarray):
    """
    Process audio using Faster-Whisper in a separate thread.
    """

    if audio.size == 0:
        return

    result = await run_in_threadpool(
        speech_service.transcribe_audio,
        audio
    )

    if result["text"]:
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

    logger.info("WebSocket connection established")

    try:

        while True:

            message = await websocket.receive()

            # Handle client disconnection
            if message["type"] == "websocket.disconnect":
                logger.info("Client disconnected")
                break

            # Receive audio bytes
            if message.get("bytes"):

                audio_chunk = np.frombuffer(
                    message["bytes"],
                    dtype=np.float32
                )

                # Validate audio data
                if audio_chunk.size == 0:
                    continue

                if not np.isfinite(audio_chunk).all():
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid audio data received"
                    })
                    continue

                # Add incoming audio to buffer
                audio_buffer = np.concatenate(
                    [audio_buffer, audio_chunk]
                )

                # Process audio in fixed-size chunks
                while len(audio_buffer) >= CHUNK_SIZE:

                    current_audio = audio_buffer[:CHUNK_SIZE]

                    audio_buffer = audio_buffer[CHUNK_SIZE:]

                    await process_audio(
                        websocket,
                        current_audio
                    )

            # Handle client commands
            elif message.get("text"):

                try:
                    command = json.loads(message["text"])

                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON command"
                    })
                    continue

                # Stop recording and process remaining audio
                if command.get("action") == "stop":

                    if len(audio_buffer) > 0:

                        await process_audio(
                            websocket,
                            audio_buffer
                        )

                        audio_buffer = np.array(
                            [],
                            dtype=np.float32
                        )

                    await websocket.send_json({
                        "type": "completed",
                        "message": "Transcription completed"
                    })

                    logger.info("Transcription completed")

                    break

    except WebSocketDisconnect:

        logger.info("WebSocket disconnected")

    except Exception as error:

        logger.exception(
            "Error during speech transcription: %s",
            error
        )

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
