import os
import tempfile

from fastapi import HTTPException, UploadFile

from server.app import app_context


async def transcribe_audio_file(file: UploadFile) -> str:
    """
    Handles transcription of the user's voice
    """
    if not app_context.WHISPER_MODEL:
        print("Error: Whisper model is not initialized.")
        raise HTTPException(500, "Whisper model is not initialized.")

    temp_audio_path = None
    try:

        original_filename = file.filename or "audio.webm"
        _, file_extension = os.path.splitext(original_filename)

        file_extension = file_extension.lower()

        if not file_extension:
            file_extension = ".webm"

        # Copies all audio content into a temp file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name

        print(
            f"Voice command received ({file_extension}), temporary file: {temp_audio_path}"
        )

        # Transcribing using out faster-whisper model
        user_text = ""
        async with app_context.MODEL_LOCK:
            print("Transcribing with Faster-Whisper...")
            # Whisper kütüphanesi dosya uzantısına bakarak formatı otomatik tanır
            segments, info = app_context.WHISPER_MODEL.transcribe(
                temp_audio_path, beam_size=5
            )
            segment_texts = [segment.text for segment in segments]
            user_text = "".join(segment_texts).strip()

        if not user_text or len(user_text.strip()) < 2:
            raise HTTPException(
                400, f"No speech detected in audio or text is too short: '{user_text}'"
            )

        return user_text

    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback

        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(500, f"Transcription error: {e}")
    finally:
        # After everything completed we delete the temp file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except Exception as e:
                print(f"Error removing temp file: {e}")
