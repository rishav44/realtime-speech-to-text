
import logging
from faster_whisper import WhisperModel
from app.core.config import settings

logger = logging.getLogger(__name__)


class SpeechService:

    def __init__(self):
        logger.info(
            "Loading Faster-Whisper model: %s",
            settings.WHISPER_MODEL
        )

        self.model = WhisperModel(
            settings.WHISPER_MODEL,
            device=settings.DEVICE,
            compute_type=settings.COMPUTE_TYPE
        )

        logger.info("Whisper model loaded successfully.")

    def transcribe_audio(self, audio):
        try:
            if audio is None or len(audio) < 16000:
                return {
                    "text": "",
                    "language": "unknown",
                    "language_probability": 0.0
                }

            segments, info = self.model.transcribe(
                audio,
                language=None,
                beam_size=3,
                vad_filter=True,
                vad_parameters={
                    "min_silence_duration_ms": 500,
                    "speech_pad_ms": 200
                },
                condition_on_previous_text=False,
                no_speech_threshold=0.6
            )

            transcription = " ".join(
                segment.text.strip()
                for segment in segments
                if segment.text.strip()
            )

            return {
                "text": transcription.strip(),
                "language": info.language or "unknown",
                "language_probability": round(
                    info.language_probability or 0.0,
                    3
                )
            }

        except Exception:
            logger.exception("Speech transcription failed")

            return {
                "text": "",
                "language": "unknown",
                "language_probability": 0.0
            }


speech_service = SpeechService()
