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
from Utilities.Check import *

client = TelegramClient(session_name, api_id, api_hash)


user_last_message_times = {}
users_waiting_for_confirmation = {}


async def is_first_message(client, chat_id, user_id, message_id):
    """Checks if a message is the first message from a specific user in a chat."""
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return True

        for message in messages:
            if message.sender_id == user_id:
                return False

        return True

    except Exception as e:
        print(f"Error checking message history: {e}")
        return False


async def is_following_first_vn(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if message.media:
                    if isinstance(message.media, MessageMediaDocument):
                        # Check if it's a document
                        document = message.media.document
                        mime_type = document.mime_type
                        size = document.size
                        document = message.media.document
                        mime_type = document.mime_type
                        size = document.size
                        # mime_type='audio/ogg', size=62571
                        if mime_type == "audio/ogg" and size == 62571:
                            return True
        return False

    except Exception as e:
        print(f"Error checking message history: {e}")
        return False


async def is_following_18_confirmation(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if message.message == CONFIRM_AFTER_FIRST_NOTE_TEXT1:
                    print("it is following 18")
                    return True

        print("not following 18")
        return False

    except Exception as e:
        print(f"Error checking message history: {e}")
        return False


async def has_broker_message_been_sent(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if message.message == BROKER_MESSAGE:
                    print("broker message has been sent before")
                    return True

        print("broker message has not been sent before")
        return False

    except Exception as e:
        print(f"Error checking message history: {e}")
        return False


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
    # check if message has text

    # check if its from the bot/source account
    print(f"is sender a bot: {sender.bot == True}")
    print(f"sender number: {sender_phone}")
    print(f"sender name: {session_name}")

    if sender.bot or sender_phone == "447592515298":
        return

    print(f"Received message from {sender.first_name}: {message_text}")

    try:
        user_last_message_times[user_id] = datetime.now()

        result = await check_message_history(client, chat_id, user_id, message_id)

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


async def check_for_chaseups(client):
    while True:
        now = datetime.now()
        users_to_remove = []

        for user_id, start_time in users_waiting_for_confirmation.items():
            if now - start_time >= CHASEUP_DELAY:
                try:
                    chat = await client.get_entity(user_id)
                    await client.send_file(chat.id, file=CHASEUP_NOTE, voice_note=True)
                    print(f"Sent chase-up voice note to user ID: {user_id}")
                    users_to_remove.append(user_id)
                except Exception as e:
                    print(f"Error sending chase-up to user ID {user_id}: {e}")

        for user_id in users_to_remove:
            del users_waiting_for_confirmation[user_id]

        await asyncio.sleep(75)


async def main_function():
    async with client:
        await client.start(phone)
        print("Client started. Waiting for messages...")
        asyncio.create_task(check_for_chaseups(client))  # Start chase-up task
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main_function())
