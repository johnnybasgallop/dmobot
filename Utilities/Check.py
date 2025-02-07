from enum import Enum

from fuzzywuzzy import fuzz
from telethon.types import MessageMediaDocument

from config import *
from main import logger

CONFIRM_TEXTS = {
    CONFIRM_AFTER_FIRST_NOTE_TEXT1.lower(),
    CONFIRM_AFTER_FIRST_NOTE_TEXT2.lower(),
    CONFIRM_AFTER_FIRST_NOTE_TEXT3.lower(),
    CONFIRM_AFTER_FIRST_NOTE_TEXT4.lower(),
}


class MessageCheckResult(Enum):
    IS_FIRST_MESSAGE = 1
    FOLLOWS_FIRST_VN = 2
    FOLLOWS_18_CONFIRMATION = 3
    NONE = 4


async def check_message_history(client, chat_id, user_id, message_id):
    """Checks the message history and returns an enum value based on the conditions."""
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return MessageCheckResult.IS_FIRST_MESSAGE

        first_message_from_user = True
        found_first_vn = False
        found_18_confirmation = False

        for message in messages:
            if message.sender_id == user_id:
                first_message_from_user = False
                # Only need to continue searching if we haven't found both conditions yet.
                if found_first_vn and found_18_confirmation:
                    break
                else:
                    continue

            if not found_first_vn or not found_18_confirmation:
                if message.sender_id != user_id:
                    if (
                        not found_first_vn
                        and message.media
                        and isinstance(message.media, MessageMediaDocument)
                    ):
                        document = message.media.document
                        if document.mime_type == "audio/ogg" and document.size == 62571:
                            found_first_vn = True

                    if await has_cmon_message_been_sent(
                        client, chat_id, user_id, message_id
                    ):
                        found_18_confirmation = True

                    else:
                        found_18_confirmation = False

        if first_message_from_user:
            return MessageCheckResult.IS_FIRST_MESSAGE
        elif found_first_vn and not found_18_confirmation:
            return MessageCheckResult.FOLLOWS_FIRST_VN
        elif found_first_vn and found_18_confirmation:
            return MessageCheckResult.FOLLOWS_18_CONFIRMATION
        else:
            return MessageCheckResult.NONE

    except Exception as e:
        logger.error(f"Error checking message history: {e}")
        return MessageCheckResult.NONE


async def has_broker_message_been_sent(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if message.message == BROKER_MESSAGE:
                    logger.info(f"broker message has been sent to @{user_id} before")
                    return True

        logger.info(f"broker message never been sent to @{user_id} before, proceeding...")
        return False

    except Exception as e:
        logger.error(f"Error checking message history: {e}")
        return False


async def has_first_vn_been_sent(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if message.media and isinstance(message.media, MessageMediaDocument):
                    document = message.media.document
                    if document.mime_type == "audio/ogg" and document.size == 62571:
                        logger.info(
                            f"found first vn in the chat with @{user_id}, will not send again"
                        )
                        return True

        logger.info(f"first vn not found in the chat with @{user_id}, proceeding...")
        return False

    except Exception as e:
        logger.error(f"Error checking message history: {e}")
        return False


async def has_cmon_message_been_sent(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if (
                    message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT1.lower()
                    or message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT2.lower()
                    or message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT3.lower()
                    or message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT4.lower()
                ):
                    logger.info(
                        f"found a cmonn message in the chat with @{user_id}, will not send again"
                    )
                    return True

        logger.info(f"no cmonn message found in chat with @{user_id}, proceeding...")

        return False

    except Exception as e:
        logger.error(f"Error checking message history: {e}")
        return False
