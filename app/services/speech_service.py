
import logging
import os

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class SpeechService:

    def __init__(self):
        logger.info("Loading Faster-Whisper model...")

        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

        logger.info("Whisper model loaded successfully.")

    def transcribe_audio(self, audio):
        try:
            if audio is None or len(audio) == 0:
                return {
                    "text": "",
                    "language": "unknown",
                    "language_probability": 0.0
                }

            # Ignore very short audio chunks
            if len(audio) < 16000:
                return {
                    "text": "",
                    "language": "unknown",
                    "language_probability": 0.0
                }

            segments, info = self.model.transcribe(
                audio,
                language=None,
                beam_size=5,
                vad_filter=True,
                vad_parameters={
                    "min_silence_duration_ms": 500,
                    "speech_pad_ms": 200
                },
                condition_on_previous_text=False,
                no_speech_threshold=0.6,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0
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
                    info.language_probability or 0.0, 3
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
