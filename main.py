import asyncio
import time
from datetime import datetime, timedelta

from fuzzywuzzy import fuzz
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Message

# Replace with your API credentials, phone number, and session name
api_id = "24173242"
api_hash = "e374a639670673451152516f5278b294"
phone = "+447592515298"  # Include country code (e.g., +1 for US)
session_name = "my_telegram_session"

FIRST_MESSAGE_VOICE_NOTE = "./voicenotes/first.ogg"

AFTER_FIRST_NOTE_TEXT1 = """You will need £300 to deposit but remember, the bigger deposit the less risk and more profit 👊🏿 have
ee, Fxcess, FXgiant, Axi or Moneta account before?"""


client = TelegramClient(session_name, api_id, api_hash)


async def is_first_message(client, chat_id, user_id, message_id):
    """Checks if a message is the first message from a specific user in a chat."""
    try:
        messages = await client.get_messages(
            chat_id,
            limit=100,
            max_id=message_id,
        )

        if not messages:
            return True

        for message in messages:
            if message.sender_id == user_id:
                return False

        return True

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
        await asyncio.sleep(5)
        await event.mark_read()

        # Checks for first message
        if await is_first_message(
            client,
            chat_id,
            user_id,
            message_id,
        ):
            print("First message from this user!")
            await asyncio.sleep(30)
            await client.send_file(
                chat_id,
                file=FIRST_MESSAGE_VOICE_NOTE,
                voice_note=True,
            )
            await asyncio.sleep(16)
            await client.send_message(chat_id, AFTER_FIRST_NOTE_TEXT1)

    except FileNotFoundError as e:
        print(f"Error: Audio file not found: {e}")
    except Exception as e:
        print(f"Error sending voice note: {e}")


# Check every hour


async def main_function():
    async with client:
        await client.start(phone)
        print("Client started. Waiting for messages...")  # Start chase-up task
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main_function())
