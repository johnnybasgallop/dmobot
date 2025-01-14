import asyncio
import time
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from fuzzywuzzy import fuzz
# Replace with your API credentials, phone number, and session name
api_id = "24173242"
api_hash = 'e374a639670673451152516f5278b294'
phone = '+447592515298'  # Include country code (e.g., +1 for US)
session_name = 'my_telegram_session'

FIRST_MESSAGE_VOICE_NOTE = "./voicenotes/1stVN.ogg"

CONFIRM_AFTER_FIRST_NOTE = "./voicenotes/AffirmAfter1st.ogg"
CONFIRM_AFTER_FIRST_NOTE_TEXT1 = """Here is the link to our recommended broker. This is where you will manage your funds! DO NOT USE THE APP, only use the broker online through link below

https://go.t4trade.com/visit/?bta=37303&brand=t4trade

You should select: 
Trading account: Fixed
Bonus: 100% Supercharged bonus 
Base: GBP 
Leverage: 1:500 

Send me a screenshot of your dashboard once your account is confirmed please (this is the main screen on your trading account)."""

CONFIRM_AFTER_FIRST_NOTE2 = "./voicenotes/AffirmAfter1st-2.ogg"
CONFIRM_AFTER_FIRST_IMG = "./voicenotes/AffirmAfter1stImg.jpg"

AFTER_SIGN_UP_NOTE = "./voicenotes/AfterSignUp.ogg"
AFTER_SIGN_UP_TO_ASSITANT_TEXT = """Yes bro it’s Jack here DMO’s assistant, The next step is to deposit your funds so we can get started tonight! £300 minimum; once the funds show on your dashboard send me a screenshot 🔥"""

IS_THIS_DMO_NOTE = "./voicenotes/IsThisDMO.ogg"
IS_THIS_SCAM_NOTE = "./voicenotes/IsThisAScam.ogg"
CHASEUP_NOTE = "./voicenotes/ChaseUp.ogg"

VOICE_NOTE_A_PATH = "./vn2.ogg"
VOICE_NOTE_B_PATH = "./vn3.ogg"

client = TelegramClient(session_name, api_id, api_hash)

affirmations = (
    "yes", "yep", "yeah", "ye", "yh", "aye", "yup", "uh-huh", "uh huh",
    "okay", "ok", "alright", "all right", "sure", "certainly", "indeed",
    "absolutely", "definitely", "agreed", "i agree", "sounds good",
    "i'm ready", "i am ready", "ready", "let's go", "lets go", "bring it on",
    "hit me", "go for it", "do it", "proceed", "start", "begin", "commence",
    "yessir", "yessirrr", "yessirr", "yessss", "yesssss", "ya", "yah",
    "word", "bet", "fosho", "fo sho", "for sure", "okey", "okayy"
)

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
    message_text = event.message.text.lower() if event.message.text else ""
     #check if message has text
    print(f"Received message from {sender.first_name}: {message_text}")

    try:
        await asyncio.sleep(3)
        await event.mark_read()

        if await is_first_message(client, chat_id, user_id, message_id):
            print("First message from this user!")
            await asyncio.sleep(2)
            await client.send_file(chat_id, file=FIRST_MESSAGE_VOICE_NOTE, voice_note=True)

        elif any(fuzz.ratio(message_text, affirmation) >= 80 for affirmation in affirmations):
            await asyncio.sleep(2)
            await client.send_file(chat_id, file=CONFIRM_AFTER_FIRST_NOTE, voice_note=True)
            print(f"Sent voice note A to {sender.first_name}")
            await asyncio.sleep(1)
            await client.send_message(chat_id, CONFIRM_AFTER_FIRST_NOTE_TEXT1)
            print(f"Sent text to {sender.first_name}")
            await asyncio.sleep(1)
            await client.send_file(chat_id, file=CONFIRM_AFTER_FIRST_IMG)
            print(f"Sent image to {sender.first_name}")
            

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