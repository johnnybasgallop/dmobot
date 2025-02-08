# Replace with your API credentials, phone number, and session name
import os
from datetime import datetime, timedelta

# api_id = os.environ.get("APP_ID")
# api_hash = os.environ.get("API_HASH")
# phone = os.environ.get("PHONE")
# phone_extension = os.environ.get("PHONE_EXTENSION")

api_id = "24173242"
api_hash = "e374a639670673451152516f5278b294"
phone = "7592515298"
phone_extension = "+44"


FIRST_MESSAGE_VOICE_NOTE = "./voicenotes/vn1.ogg"

CONFIRM_AFTER_FIRST_NOTE = "./voicenotes/AffirmAfter1st.ogg"
CONFIRM_AFTER_FIRST_NOTE_TEXT1 = """CMONN are you 18? you will need MINIMUM £300 to deposit but remember, the bigger deposit the less risk and more profit! is that cool?"""
CONFIRM_AFTER_FIRST_NOTE_TEXT2 = """CMONN you will need £300 Minimum to deposit but remember, the bigger deposit the less risk and more profit, this is for our most ELITE group out of the 4 👊🏼 Have you ever had a trading account with Moneta?"""
CONFIRM_AFTER_FIRST_NOTE_TEXT3 = """JUST REMEMBER you need to be over 18 and have a minimum of £300 ready to invest today! Remember the more you have in account the less you risk and the more you can make!! Have you ever had a T4trade, Fxcess, FXgiant, Axi or moneta account before?"""
CONFIRM_AFTER_FIRST_NOTE_TEXT4 = """CMONN you will need MINIMUM £300 to deposit but remember, the bigger deposit the less risk and more profit, this is for our most ELITE group out of the 4 👊🏼 Have you ever had a trading account with Moneta?"""

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

CHASEUP_NOTE = "./voicenotes/ChaseUp.ogg"

CHASEUP_DELAY = timedelta(seconds=1800)
