from fastapi import APIRouter, UploadFile, File, HTTPException
import logging

from server.app.helpers import transcribe_audio_file, analyze_intent
from server.app.connection_manager import manager

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
async def transcribe_voice(file: UploadFile = File(...)):
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
            logger.info(f"Routing command '{command}' to '{target_client}' with payload '{message}'")
            
            # Helper function in manager handles sending to specific client
            await manager.send_message(message, target_client)
        else:
            logger.info(f"No direct device command found for: {command}")

        return {"text": transcription, "intent": intent}
        
    except Exception as e:
        logger.error(f"Transcribe/Process error: {e}")
        raise HTTPException(500, f"Transcribe error: {e}")
