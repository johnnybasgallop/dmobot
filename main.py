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

# Replace with your API credentials, phone number, and session name
api_id = "24173242"
api_hash = "e374a639670673451152516f5278b294"
phone = "+447592515298"  # Include country code (e.g., +1 for US)
session_name = "my_telegram_session"

FIRST_MESSAGE_VOICE_NOTE = "./voicenotes/vn1.ogg.ogg"

CONFIRM_AFTER_FIRST_NOTE = "./voicenotes/AffirmAfter1st.ogg"
CONFIRM_AFTER_FIRST_NOTE_TEXT1 = """CMONN are you 18? you will need MINIMUM £300 to deposit but remember, the bigger deposit the less risk and more profit! is that cool?"""
BROKER_MESSAGE = """Perfect, here is the link to our recommended broker. This is where you will manage your funds! PLEASE make sure to only use the broker through our link below

https://go.monetamarkets.com/visit/?bta=37949&brand=monetamarkets

You should select:
Trading platform: MT4
Trading account: Direct STP
Base: GBP/EUR/USD
Leverage: 1:500

Send me a screenshot of your dashboard once your account is confirmed please (this is the main screen on your trading account)."""

CONFIRM_AFTER_FIRST_NOTE2 = "./voicenotes/AffirmAfter1st-2.ogg"
CONFIRM_AFTER_FIRST_IMG = "./voicenotes/AffirmAfter1stImg.jpg"

AFTER_SIGN_UP_NOTE = "./voicenotes/AfterSignUp.ogg"

CHASEUP_NOTE = "./voicenotes/ChaseUp.ogg"


client = TelegramClient(session_name, api_id, api_hash)


CHASEUP_DELAY = timedelta(seconds=75)
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


# TODO: write this function to check if the intro VN has been sent and the affirmitive message is for that
# *Done
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


# TODO: write this function to check if the "Are you 18" message has been sent and the affirmitive message is for that
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


# TODO: ensure this works for multiple chats
# function to pin chats when things go wrong etc.
# async def pin_chat(client, chat_id, user_id):
#     try:
#         print("Attempting to pin chat")
#         chat = await client.get_entity(chat_id)

#         # Pin the chat using PinDialogRequest
#         # Get currently pinned chats
#         dialogs = await client.get_dialogs()
#         pinned_dialogs = [
#             InputDialogPeer(dialog.entity) for dialog in dialogs if dialog.pinned
#         ]

#         # Add the new chat to the pinned list
#         if InputDialogPeer(chat) not in pinned_dialogs:
#             pinned_dialogs.insert(0, InputDialogPeer(chat))  # Insert at the top

#         # Reorder the pinned dialogs with the updated list
#         await client(
#             ReorderPinnedDialogsRequest(folder_id=1, order=pinned_dialogs)
#         )  # Set to False to unpin

#     except Exception as e:
#         print(f"Error checking message history: {e}")
#         return False


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
        await asyncio.sleep(3)
        await event.mark_read()
        user_last_message_times[user_id] = datetime.now()

        # Checks for first message
        if await is_first_message(client, chat_id, user_id, message_id):
            print("First message from this user!")
            await asyncio.sleep(2)
            await client.send_file(
                chat_id, file=FIRST_MESSAGE_VOICE_NOTE, voice_note=True
            )

        elif isinstance(event.message, Message) and event.message.media:
            if event.message.media.photo or event.message.media.video:

                if user_id in users_waiting_for_confirmation:
                    del users_waiting_for_confirmation[user_id]

                print(f"Received image from {sender.first_name} - Confirmation received!")
                print(
                    f"Received likely confirmation image/video from {sender.first_name}"
                )

                await asyncio.sleep(3)
                # await client.send_file(chat_id, file=AFTER_SIGN_UP_NOTE, voice_note=True)
                # Pin the user
                await asyncio.sleep(5)
                return
        # Checks for affirmations e.g. ('Yes' or "lets go" etc.) and sends voicenotes and texts with signup instructions
        # May need to add in a check to make sure that the the confirm_after_first_note text isnt in the chat history, so that this only gets sent once.
        elif any(
            fuzz.ratio(message_text, affirmation) >= 80 for affirmation in affirmations
        ):
            await asyncio.sleep(1)
            await client.send_message(chat_id, CONFIRM_AFTER_FIRST_NOTE_TEXT1)
            await is_following_first_vn(client, chat_id, user_id, message_id)
            await is_following_18_confirmation(client, chat_id, user_id, message_id)
            users_waiting_for_confirmation[user_id] = datetime.now()
            print(
                f"1 hour countdown to chaseup has been started for {sender.first_name} | countdown will end when we receive proof of signup"
            )

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

        await asyncio.sleep(75)  # Check every hour


async def main_function():
    async with client:
        await client.start(phone)
        print("Client started. Waiting for messages...")
        asyncio.create_task(check_for_chaseups(client))  # Start chase-up task
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main_function())
