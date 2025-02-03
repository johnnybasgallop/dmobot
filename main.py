import asyncio
import logging
import os
import time
from datetime import datetime, timedelta

from fuzzywuzzy import fuzz
from logtail import LogtailHandler
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest, ReorderPinnedDialogsRequest
from telethon.tl.types import (
    InputDialogPeer,
    InputPeerChat,
    Message,
    MessageMediaDocument,
)

from affirmations import affirmations
from config import *
from Utilities.ChaseupCheck import *
from Utilities.Check import *

# Get the Logtail Source Token from the environment variable
LOGTAIL_TOKEN = os.environ.get("LOGTAIL_TOKEN")

# Configure the logger
logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.DEBUG)  # Set the logger's level to DEBUG

# Configure Logtail handler to capture ERROR and above
if LOGTAIL_TOKEN:
    logtail_handler = LogtailHandler(source_token=LOGTAIL_TOKEN)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logtail_handler.setFormatter(formatter)
    logtail_handler.setLevel(logging.ERROR)  # Set Logtail handler level to ERROR
    logger.addHandler(logtail_handler)

# Configure StreamHandler to capture INFO and above
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
console_handler.setLevel(logging.INFO)  # Set console handler level to INFO
logger.addHandler(console_handler)

client = TelegramClient(session_name, api_id, api_hash)


@client.on(events.NewMessage)
async def my_event_handler(event):
    sender = await event.get_sender()
    sender_phone = getattr(sender, "phone", None)
    if sender is None or sender.bot:  # check sender exists
        return  # Ignore bots and channel posts

    chat = await event.get_chat()
    if chat is None:
        return  # ignore if no chat
    chat_id = chat.id
    user_id = event.sender_id
    message_id = event.message.id
    message_text = event.message.text.lower() if event.message.text else ""

    if sender.bot or sender_phone == f"44{phone}":
        return

    try:
        user_last_message_times[user_id] = datetime.now()

        result = await check_message_history(client, chat_id, user_id, message_id)
        if result == MessageCheckResult.IS_FIRST_MESSAGE:
            logger.info(f"Received fist message from {session_name} @ {sender_phone}")
            await asyncio.sleep(2)
            await event.mark_read()
            logger.info(f"Sending {session_name} @ {sender_phone} the first voicenote")
            await client.send_file(
                chat_id, file=FIRST_MESSAGE_VOICE_NOTE, voice_note=True
            )
            logger.info(f"Sent {session_name} @ {sender_phone} the first voicenote")

        elif any(
            fuzz.ratio(message_text, affirmation) >= 80 for affirmation in affirmations
        ) or any(
            word in message_text
            for word in [
                "yeah",
                "yes",
                "ready",
                "18",
                "over",
                "yeh",
                "yh",
                "yup",
                "start",
                "started",
            ]
        ):

            if result == MessageCheckResult.FOLLOWS_FIRST_VN:
                logger.info(
                    f"Received Likely Second Affirmation message following first VN from {session_name} @ {sender_phone}"
                )
                await asyncio.sleep(2)
                await event.mark_read()
                logger.info(f"Sending {session_name} @ {sender_phone} the follow up text")
                await client.send_message(chat_id, CONFIRM_AFTER_FIRST_NOTE_TEXT1)
                logger.info(f"Sent {session_name} @ {sender_phone} the follow up text")
            elif (
                result == MessageCheckResult.FOLLOWS_18_CONFIRMATION
                and not await has_broker_message_been_sent(
                    client, chat_id, user_id, message_id
                )
            ):
                logger.info(
                    f"Received likely confirmation after 2nd follow up message from {session_name} @ {sender_phone}"
                )
                await asyncio.sleep(2)
                await event.mark_read()
                logger.info(f"Sending {session_name} @ {sender_phone} the broker message")
                await client.send_message(chat_id, BROKER_MESSAGE)
                logger.info(f"Sent {session_name} @ {sender_phone} the broker message")
                logger.info(
                    f"Adding {session_name} @ {sender_phone} to the chaseup countdown"
                )
                users_waiting_for_confirmation[user_id] = datetime.now()
                logger.info(
                    f"1 hour countdown to chaseup has been started for {sender.first_name} @ {sender_phone} | countdown will end when we receive proof of signup"
                )
                logger.info(
                    f"Sending {session_name} @ {sender_phone} the proof voicenote"
                )
                await client.send_file(
                    chat_id, file=CONFIRM_AFTER_FIRST_NOTE2, voice_note=True
                )
                logger.info(f"Sent {session_name} @ {sender_phone} the proof voicenote")
                logger.info(f"Sending {session_name} @ {sender_phone} the proof image")
                await client.send_file(chat_id, file=CONFIRM_AFTER_FIRST_IMG)
                logger.info(f"Sent {session_name} @ {sender_phone} the proof image")

        elif isinstance(event.message, Message) and event.message.media:
            if event.message.media.photo or event.message.media.video:
                logger.info(
                    f"Received an image or video from {session_name} @ {sender_phone} Assuming this is a confirmation"
                )
                await asyncio.sleep(6)
                await event.mark_read()
                if user_id in users_waiting_for_confirmation:
                    logger.info(
                        f"Removing user {session_name} @ {sender_phone} from followup list"
                    )
                    del users_waiting_for_confirmation[user_id]
                    logger.info(
                        f"User {session_name} @ {sender_phone} Has been removed from the followup list"
                    )

                await asyncio.sleep(3)
                return

        else:
            logger.info(
                f"unknown command/input {message_text} from {session_name} @ {sender_phone}"
            )

    except FileNotFoundError as e:
        logger.error(f"Error: Audio file not found: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error sending voice note: {e}", exc_info=True)


async def main_function():
    async with client:
        await client.start(f"{phone_extension}{phone}")
        logger.info("Client started. Waiting for messages...")
        asyncio.create_task(check_for_chaseups(client))  # Start chase-up task
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main_function())
