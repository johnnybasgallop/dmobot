import asyncio
from datetime import datetime, timedelta

from config import *
from main import logger

user_last_message_times = {}
users_waiting_for_confirmation = {}


async def check_for_chaseups(client):
    while True:
        now = datetime.now()
        users_to_remove = []

        for user_id, start_time in users_waiting_for_confirmation.items():
            if now - start_time >= CHASEUP_DELAY:
                try:
                    chat = await client.get_entity(user_id)
                    await client.send_file(chat.id, file=CHASEUP_NOTE, voice_note=True)
                    logger.info(f"Sent chase-up voice note to user id: {user_id}")
                    users_to_remove.append(user_id)
                except Exception as e:
                    logger.error(
                        f"Error sending chase-up to user userid: {user_id}: {e}",
                        exc_info=True,
                    )

        for user_id in users_to_remove:
            logger.info(
                f"Removing user (userid) {user_id} from chaseup list since chaseup vn has been sent"
            )
            del users_waiting_for_confirmation[user_id]

        await asyncio.sleep(75)
