import asyncio
import time
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest

# Replace with your API credentials, phone number, and session name
api_id = "24173242"
api_hash = 'e374a639670673451152516f5278b294'
phone = '+447592515298'  # Include country code (e.g., +1 for US)
session_name = 'my_telegram_session'

FIRST_MESSAGE_VOICE_NOTE = "./vn1b.ogg"
VOICE_NOTE_A_PATH = "./vn2.ogg"
VOICE_NOTE_B_PATH = "./vn3.ogg"

client = TelegramClient(session_name, api_id, api_hash)

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

@client.on(events.NewMessage)
async def my_event_handler(event):
    sender = await event.get_sender()
    if sender is None or sender.bot: #check sender exists
        return  # Ignore bots and channel posts

    chat = await event.get_chat()
    if chat is None:
        return #ignore if no chat
    chat_id = chat.id
    user_id = event.sender_id
    message_id = event.message.id
    message_text = event.message.text.lower() if event.message.text else "" #check if message has text
    print(f"Received message from {sender.first_name}: {message_text}")
    try:
        await asyncio.sleep(2)
        await event.mark_read()
        await asyncio.sleep(4)
        if await is_first_message(client, chat_id, user_id, message_id):
            print("First message from this user!")
            await client.send_file(chat_id, file=FIRST_MESSAGE_VOICE_NOTE, voice_note=True)
        elif message_text == "yes":
            await client.send_file(chat_id, file=VOICE_NOTE_A_PATH, voice_note=True)
            print(f"Sent voice note A to {sender.first_name}")
        elif message_text == "i want to make money":
            await client.send_file(chat_id, file=VOICE_NOTE_B_PATH, voice_note=True)
            print(f"Sent voice note B to {sender.first_name}")
        else:
            print(f"Unknown message. No voice note sent.")
    except FileNotFoundError as e:
        print(f"Error: Audio file not found: {e}")
    except Exception as e:
        print(f"Error sending voice note: {e}")

async def main_function(): #added this so the client is used within a with statement
    async with client:
        await client.start(phone)
        print("Client started. Waiting for messages...")
        await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main_function())