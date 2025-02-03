# Replace with your API credentials, phone number, and session name
from datetime import datetime, timedelta

api_id = "24173242"
api_hash = "e374a639670673451152516f5278b294"
phone = "+447453904944"  # Include country code (e.g., +1 for US)
session_name = "my_telegram_session"

FIRST_MESSAGE_VOICE_NOTE = "./voicenotes/vn1.ogg"

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

CONFIRM_AFTER_FIRST_NOTE2 = "./voicenotes/ProofVN.ogg"
CONFIRM_AFTER_FIRST_IMG = "./voicenotes/AffirmAfter_18_confirmation.jpg"

AFTER_SIGN_UP_NOTE = "./voicenotes/AfterSignUp.ogg"

CHASEUP_NOTE = "./voicenotes/ChaseUp.ogg"

CHASEUP_DELAY = timedelta(seconds=75)
