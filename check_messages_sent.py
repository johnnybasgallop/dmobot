async def check_messages_sent(client, chat_id):
    """
    Checks a Telegram chat history for specific messages sent *by the current user*.

    Args:
        client: The Telethon client.
        chat_id: The ID of the chat to check (can be a username, phone number, or chat ID).

    Returns:
        A set of strings, where each string is a message that has already been sent.

    Raises:
        ValueError: If the Telethon client cannot connect or authenticate,
                    or if the chat_id is invalid.
        TypeError: If api_id is not an int.
    """
    import os

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

    sent_messages = set()

    try:
        chat_entity = await client.get_entity(chat_id)
        chat_id = chat_entity.id  # Get the numeric ID
    except ValueError as e:
        raise ValueError(f"Invalid chat_id: {chat_id}. {e}") from e
    except Exception as e:
        raise

    async for message in client.iter_messages(
        chat_id, from_user="me"
    ):  # Only check *our* messages
        if message.text and message.text in BOT_MESSAGES:
            sent_messages.add(message.text)
        elif message.voice and message.file and message.file.name:
            for msg_check in BOT_MESSAGES:
                if message.file.name == os.path.basename(msg_check):
                    sent_messages.add(msg_check)
        elif message.photo and message.file and message.file.name:
            for msg_check in BOT_MESSAGES:
                if message.file.name == os.path.basename(msg_check):
                    sent_messages.add(msg_check)
    return sent_messages
