import os

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument

# Put all messages that the BOT sends here.  TEXT and FILE PATHS.
BOT_MESSAGES = {
    "./voicenotes/vn1.ogg",
    "./voicenotes/AffirmAfter1st.ogg",
    """CMONN are you 18? you will need MINIMUM £300 to deposit but remember, the bigger deposit the less risk and more profit! is that cool?""",
    """CMONN you will need £300 Minimum to deposit but remember, the bigger deposit the less risk and more profit, this is for our most ELITE group out of the 4 👊🏼 Have you ever had a trading account with Moneta?""",
    """JUST REMEMBER you need to be over 18 and have a minimum of £300 ready to invest today! Remember the more you have in account the less you risk and the more you can make!! Have you ever had a T4trade, Fxcess, FXgiant, Axi or moneta account before?""",
    """CMONN you will need MINIMUM £300 to deposit but remember, the bigger deposit the less risk and more profit, this is for our most ELITE group out of the 4 👊🏼 Have you ever had a trading account with Moneta?""",
    """Perfect, here is the link to our recommended broker. This is where you will manage your funds! PLEASE make sure to only use the broker through our link below

https://go.monetamarkets.com/visit/?bta=37949&brand=monetamarkets

You should select:
Trading platform: MT4
Trading account: Direct STP
Base: GBP/EUR/USD
Leverage: 1:500

Send me a screenshot of your dashboard once your account is confirmed please (this is the main screen on your trading account).""",
    "./voicenotes/ProofVN.ogg",
    "./voicenotes/AffirmAfter_18_confirmation.jpg",
    "./voicenotes/AfterSignUp.ogg",
    "./voicenotes/ChaseUp.ogg",
}


async def check_for_manual_intervention(client: TelegramClient, chat_id: str) -> bool:
    """
    Checks if the last 100 messages sent *by the bot* in a chat include any messages
    *not* present in the BOT_MESSAGES set.

    Args:
        client: The Telethon client.
        chat_id: The ID of the chat to check (can be a username, phone number, or chat ID).

    Returns:
        True if a manual intervention (a message NOT in BOT_MESSAGES) is detected,
        False otherwise (all messages within the limit are known bot messages).

    Raises:
        ValueError: If the Telethon client cannot connect or authenticate,
                    or if the chat_id is invalid.
    """
    try:
        chat_entity = await client.get_entity(chat_id)
        chat_id = chat_entity.id  # Get the numeric ID
    except ValueError as e:
        raise ValueError(f"Invalid chat_id: {chat_id}. {e}") from e
    except Exception as e:
        raise

    async for message in client.iter_messages(
        chat_id, from_user="me", limit=100
    ):  # Only our messages
        if message.text and message.text not in BOT_MESSAGES:
            return True  # Found a manual text message
        elif message.voice and message.file and message.file.name:
            found = False
            for msg_check in BOT_MESSAGES:
                if message.file.name == os.path.basename(msg_check):
                    found = True
                    break
            if not found:
                return True  # Found a manual voice note
        elif message.photo and message.file and message.file.name:
            found = False
            for msg_check in BOT_MESSAGES:
                if message.file.name == os.path.basename(msg_check):
                    found = True
                    break
            if not found:
                return True  # Found a manual photo
        # Add checks for other media types as needed (videos, documents, etc.)

    return False  # No manual messages found within the last 100 messages
