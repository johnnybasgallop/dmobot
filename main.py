import asyncio
import time
from telethon import TelegramClient, events

# Replace with your API credentials, phone number, and session name
api_id = "24173242"
api_hash = 'e374a639670673451152516f5278b294'
phone = '+447592515298'  # Include country code (e.g., +1 for US)
session_name = 'my_telegram_session'

AUDIO_FILE_PATH = "./testingmp3.ogg"  # Replace with the actual path

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except telethon.errors.SessionPasswordNeededError:
            await client.sign_in(password=input('Two-step verification password: '))

    @client.on(events.NewMessage)
    async def my_event_handler(event):
        sender = await event.get_sender()
        if sender.bot:
            return  # Ignore bots

        print(f"Received {event.message.text} from {sender.first_name}")
        await asyncio.sleep(5)

        try:
            await client.send_file(
                event.chat_id,  # Send to the same chat where the message came from
                file=AUDIO_FILE_PATH,
                voice_note=True  # This is the crucial line!
            )
            print(f"Sent voice note reply to {sender.first_name}")
        except FileNotFoundError:
            print(f"Error: Audio file not found at {AUDIO_FILE_PATH}")
        except Exception as e:
            print(f"Error sending voice note: {e}")

    print("Client started. Waiting for messages...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())