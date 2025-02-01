import asyncio
import time
from datetime import datetime, timedelta

from fuzzywuzzy import fuzz
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

    print(f"Received message from {sender.first_name}: {message_text}")

    try:
        user_last_message_times[user_id] = datetime.now()

        result = await check_message_history(client, chat_id, user_id, message_id)
        print(f"result: {result}")
        if result == MessageCheckResult.IS_FIRST_MESSAGE:
            print("This is the first message from the user.")
            await asyncio.sleep(2)
            await event.mark_read()
            await client.send_file(
                chat_id, file=FIRST_MESSAGE_VOICE_NOTE, voice_note=True
            )

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
                await asyncio.sleep(2)
                await event.mark_read()
                await client.send_message(chat_id, CONFIRM_AFTER_FIRST_NOTE_TEXT1)

            elif (
                result == MessageCheckResult.FOLLOWS_18_CONFIRMATION
                and not await has_broker_message_been_sent(
                    client, chat_id, user_id, message_id
                )
            ):
                await asyncio.sleep(2)
                await event.mark_read()
                await client.send_message(chat_id, BROKER_MESSAGE)
                users_waiting_for_confirmation[user_id] = datetime.now()
                print(
                    f"1 hour countdown to chaseup has been started for {sender.first_name} | countdown will end when we receive proof of signup"
                )
                await client.send_file(
                    chat_id, file=CONFIRM_AFTER_FIRST_NOTE2, voice_note=True
                )
                await client.send_file(chat_id, file=CONFIRM_AFTER_FIRST_IMG)

        elif isinstance(event.message, Message) and event.message.media:
            if event.message.media.photo or event.message.media.video:
                await asyncio.sleep(6)
                await event.mark_read()
                if user_id in users_waiting_for_confirmation:
                    del users_waiting_for_confirmation[user_id]

                print(f"Received image from {sender.first_name} - Confirmation received!")
                print(
                    f"Received likely confirmation image/video from {sender.first_name}"
                )

                await asyncio.sleep(3)
                return

        else:
            print("unknown command/input")

    except FileNotFoundError as e:
        print(f"Error: Audio file not found: {e}")
    except Exception as e:
        print(f"Error sending voice note: {e}")


async def main_function():
    async with client:
        await client.start(f"{phone_extension}{phone}")
        print("Client started. Waiting for messages...")
        asyncio.create_task(check_for_chaseups(client))  # Start chase-up task
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main_function())
