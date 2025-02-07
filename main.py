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
from denials import *
from manual_check import *
from Utilities.ChaseupCheck import *
from Utilities.Check import *

# Get the Logtail Source Token from the environment variable
# LOGTAIL_TOKEN = os.environ.get("LOGTAIL_TOKEN")

# Configure the logger
logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.INFO)  # Set the logger's level to DEBUG

# Configure Logtail handler to capture ERROR and above
# if LOGTAIL_TOKEN:
#     logtail_handler = LogtailHandler(
#         source_token=LOGTAIL_TOKEN,
#         host="https://in.logs.betterstack.com",
#     )
#     formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#     logtail_handler.setFormatter(formatter)
#     logtail_handler.setLevel(logging.ERROR)  # Set Logtail handler level to ERROR
#     logger.addHandler(logtail_handler)

# # Configure StreamHandler to capture INFO and above
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(
#     logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# )
# console_handler.setLevel(logging.INFO)  # Set console handler level to INFO
# logger.addHandler(console_handler)

api_id = "24173242"
api_hash = "e374a639670673451152516f5278b294"
phone = "7592515298"
phone_extension = "+44"

client = TelegramClient(None, api_id, api_hash)


@client.on(events.NewMessage)
async def my_event_handler(event):
    sender = await event.get_sender()
    sender_phone = getattr(sender, "phone", None)

    chat = await event.get_chat()
    if chat is None:
        return  # ignore if no chat
    chat_id = chat.id
    user_id = event.sender_id
    message_id = event.message.id
    message_text = event.message.text.lower() if event.message.text else ""
    # checks if sender is the bot

    print(f"message sent from: {user_id}")

    if await check_for_manual_intervention(client=client, chat_id=chat_id):
        return

    if sender.bot or sender_phone == f"44{phone}":
        return

    if any(word in message_text.lower() for word in ["gold", "platinum", "vip"]):
        return

    try:
        user_last_message_times[user_id] = datetime.now()

        result = await check_message_history(client, chat_id, user_id, message_id)

        if (
            result == MessageCheckResult.IS_FIRST_MESSAGE
            and not await has_first_vn_been_sent(client, chat_id, user_id, message_id)
        ):
            logger.info(f"Received first message {message_text} from @ userid:{user_id}")
            await asyncio.sleep(2)
            await event.mark_read()
            await asyncio.sleep(2)
            logger.info(f"Sending @ {user_id} the first voicenote")
            await client.send_file(
                chat_id, file=FIRST_MESSAGE_VOICE_NOTE, voice_note=True
            )
            logger.info(f"Sent @ {user_id} the first voicenote")

        elif (
            any(
                fuzz.ratio(message_text, affirmation) >= 80
                for affirmation in affirmations
            )
            or any(
                word in message_text
                for word in [
                    "yeah",
                    "yes",
                    "ready",
                    "over",
                    "yeh",
                    "yh",
                    "yup",
                    "start",
                    "started",
                    "okay",
                    "on it",
                    "im down",
                    "no probs",
                    "yeah calm",
                    "calm",
                    "sn",
                    "snm",
                    "fine",
                    "ok",
                    "thats fine",
                    "sound",
                ]
            )
            and not any(
                fuzz.partial_ratio(message_text, phrase) >= 85
                for phrase in no_money_phrases
            )
            and not any(
                denial in message_text
                for denial in ["11", "12", "13", "14", "15", "16", "17"]
            )
        ):

            if (
                result == MessageCheckResult.FOLLOWS_FIRST_VN
                and not await has_broker_message_been_sent(
                    client, chat_id, user_id, message_id
                )
                and not await has_cmon_message_been_sent(
                    client, chat_id, user_id, message_id
                )
            ):
                logger.info(
                    f"Received Likely Second Affirmation message: {message_text} following first VN from @ {user_id}"
                )
                await asyncio.sleep(2)
                await event.mark_read()
                await asyncio.sleep(2)
                logger.info(f"Sending @ {user_id} the follow up text")
                await client.send_message(chat_id, CONFIRM_AFTER_FIRST_NOTE_TEXT1)
                logger.info(f"Sent @ {user_id} the follow up text")
            elif (
                result == MessageCheckResult.FOLLOWS_18_CONFIRMATION
                and not await has_broker_message_been_sent(
                    client, chat_id, user_id, message_id
                )
            ):
                logger.info(
                    f"Received likely confirmation: {message_text} after 2nd follow up message from @ {user_id}"
                )
                await asyncio.sleep(2)
                await event.mark_read()
                await asyncio.sleep(2)
                logger.info(f"Sending @ {user_id} the broker message")
                await client.send_message(chat_id, BROKER_MESSAGE)
                logger.info(f"Sent @ {user_id} the broker message")
                logger.info(f"Adding @ {user_id} to the chaseup countdown")
                users_waiting_for_confirmation[user_id] = datetime.now()
                logger.info(
                    f"1 hour countdown to chaseup has been started for {sender.first_name} @ {user_id} | countdown will end when we receive proof of signup"
                )
                logger.info(f"Sending @ {user_id} the proof voicenote")
                await asyncio.sleep(2)
                await client.send_file(
                    chat_id, file=CONFIRM_AFTER_FIRST_NOTE2, voice_note=True
                )
                logger.info(f"Sent @ {user_id} the proof voicenote")
                await asyncio.sleep(2)
                logger.info(f"Sending @ {user_id} the proof image")
                await client.send_file(chat_id, file=CONFIRM_AFTER_FIRST_IMG)
                logger.info(f"Sent @ {user_id} the proof image")

        elif isinstance(event.message, Message) and event.message.media:
            if event.message.media.photo or event.message.media.video:
                logger.info(
                    f"Received an image or video from @ {user_id} Assuming this is a confirmation"
                )
                await asyncio.sleep(2)
                if user_id in users_waiting_for_confirmation:
                    logger.info(f"Removing user @ {user_id} from followup list")
                    del users_waiting_for_confirmation[user_id]
                    logger.info(
                        f"User @ {user_id} Has been removed from the followup list"
                    )

                await asyncio.sleep(2)
                return

        elif any(
            fuzz.partial_ratio(message_text, phrase) >= 85 for phrase in no_money_phrases
        ):
            logger.info(
                f"input {message_text} from @ {user_id} suggests too little money to continue or does not want to"
            )

        else:
            logger.info(f"unknown command/input {message_text} from @ {user_id}")

    except FileNotFoundError as e:
        logger.error(f"Error: Audio file not found: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error sending voice note: {e}", exc_info=True)


async def main_function():
    async with client:
        await client.start(f"{phone_extension}{phone}")
        print(f"Client started. {phone_extension}{phone} Waiting for messages...")
        asyncio.create_task(check_for_chaseups(client))  # Start chase-up task
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main_function())
