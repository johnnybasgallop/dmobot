from enum import Enum

from telethon.types import MessageMediaDocument

from config import *


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

                    if (
                        not found_18_confirmation
                        and message.message == CONFIRM_AFTER_FIRST_NOTE_TEXT1
                    ):
                        found_18_confirmation = True

        if first_message_from_user:
            return MessageCheckResult.IS_FIRST_MESSAGE
        elif found_first_vn and not found_18_confirmation:
            return MessageCheckResult.FOLLOWS_FIRST_VN
        elif found_first_vn and found_18_confirmation:
            return MessageCheckResult.FOLLOWS_18_CONFIRMATION
        else:
            return MessageCheckResult.NONE

    except Exception as e:
        print(f"Error checking message history: {e}")
        return MessageCheckResult.NONE


async def has_broker_message_been_sent(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if message.message == BROKER_MESSAGE:
                    print("broker message has been sent before")
                    return True

        print("broker message has not been sent before")
        return False

    except Exception as e:
        print(f"Error checking message history: {e}")
        return False


async def has_cmon_message_been_sent(client, chat_id, user_id, message_id):
    try:
        messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

        if not messages:
            return False

        for message in messages:
            if message.sender_id != user_id:
                if message.message == CONFIRM_AFTER_FIRST_NOTE_TEXT1:
                    print("cmon message has been sent before")
                    return True

        print("cmon message has not been sent before")
        return False

    except Exception as e:
        print(f"Error checking message history: {e}")
        return False
