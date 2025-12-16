from fastapi import APIRouter, UploadFile, File, HTTPException, Response
import logging

from ..helpers import transcribe_audio_file, analyze_intent, generate_speech
from ..connection_manager import manager

router = APIRouter()
logger = logging.getLogger("app")

# channel_id, message
COMMAND_MAP = {
    "klima_ac": ("air_conditioner_client", "1"),
    "klima_kapa": ("air_conditioner_client", "0"),
    "isik_ac": ("all_house_lights", "1"),
    "isik_kapa": ("all_house_lights", "0"),
    "kahve_ac": ("coffee_machine_client", "1"),
    "kahve_kapa": ("coffee_machine_client", "0"),
    "muzik_ac": ("speaker_group_client", "1"),
    "muzik_kapa": ("speaker_group_client", "0"),
    "televizyon_ac": ("television_client", "1"),
    "televizyon_kapa": ("television_client", "0"),
}


@router.post("/voice-message")
async def handle_voice_message(file: UploadFile = File(...)):
    try:
        # Transcribe
        transcription = await transcribe_audio_file(file)
        if not transcription:
            raise HTTPException(500, "Too short to transcribe")

        # Analyze Intent
        logger.info(f"Thinking about: {transcription}")
        intent = analyze_intent(transcription)
        logger.info(f"Intent detected: {intent}")

        command = intent.get("command")

        # Route Command via WebSocket
        if command and command in COMMAND_MAP:
            target_client, message = COMMAND_MAP[command]
            logger.info(
                f"Routing command '{command}' to '{target_client}' with payload '{message}'"
            )

            # Helper function in manager handles sending to specific client
            await manager.send_message(message, target_client)
        else:
            logger.info(f"No direct device command found for: {command}")

        # 4. Generate Audio Reply
        reply_text = intent.get("reply")
        audio_content = None
        if reply_text:
            logger.info(f"Generating speech for reply: {reply_text}")
            audio_content = generate_speech(reply_text)

        if audio_content:
            return Response(content=audio_content, media_type="audio/wav")
        else:
            # Fallback if TTS fails (or no reply), though user asked for audio only.
            # Returning 500 might be appropriate if audio is strictly required,
            # but let's return JSON with error or just the JSON as fallback.
            # User said "post'ta return olarak sadece ses dosyası olacak".
            # If we fail, maybe 500 is safer to signal Unity something went wrong.
            logger.error("Failed to generate audio content")
            raise HTTPException(500, "Failed to generate audio response")

    except Exception as e:
        logger.error(f"Transcribe/Process error: {e}")
        raise HTTPException(500, f"Transcribe error: {e}")
