from enum import Enum

from fuzzywuzzy import fuzz
from telethon.types import MessageMediaDocument

from config import *

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
        print(f"userid = {user_id}")
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
        print(f"Error checking message history: {e}")
        return MessageCheckResult.NONE


async def has_broker_message_been_sent(client, chat_id, user_id, message_id):
    try:
        print(f"userid = {user_id}")
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
        print(f"userid = {user_id}")
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
                    print("cmon message has been sent before")
                    return True

        print("cmon message has not been sent before")
        return False

    except Exception as e:
        print(f"Error checking message history: {e}")
        return False


# async def is_message_manual(client, chat_id, user_id, message_id, sender_id):
#     try:
#         print(f"sender_id = {sender_id}")
#         messages = await client.get_messages(chat_id, limit=100, max_id=message_id)

#         if not messages:
#             return False

#         for message in messages:
#             if message.sender_id == sender_id:
#                 if await is_text_manual(message=message) or await is_media_manual(
#                     message=message
#                 ):
#                     print(f"message {message.message.lower()} is manual")
#                     return True
#         return False

#     except Exception as e:
#         print(f"Error checking message history: {e}")
#         return False


# async def is_text_manual(message):
#     try:
#         if (
#             message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT1.lower()
#             or message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT2.lower()
#             or message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT3.lower()
#             or message.message.lower() == CONFIRM_AFTER_FIRST_NOTE_TEXT4.lower()
#             or any(
#                 fuzz.partial_ratio(message.message.lower(), phrase) >= 80
#                 for phrase in CONFIRM_TEXTS
#             )
#             or message.message.lower() == BROKER_MESSAGE.lower()
#         ):
#             print(f"{message.message.lower()} is not a bot text")
#             return False
#         else:
#             return True

#     except Exception as e:
#         print(f"Error checking message history: {e}")
#         return False


# async def is_media_manual(message):
#     try:
#         vn1_size = os.path.getsize(FIRST_MESSAGE_VOICE_NOTE)
#         vn2_size = os.path.getsize(CONFIRM_AFTER_FIRST_NOTE2)
#         vn3_size = os.path.getsize(CHASEUP_NOTE)

#         if message.media and isinstance(message.media, MessageMediaDocument):
#             document = message.media.document
#             if document.mime_type == "audio/ogg":
#                 if (
#                     document.size == vn1_size
#                     or document.size == vn2_size
#                     or document.size == vn3_size
#                 ):
#                     print(f"{message.message.lower()} is not a bot vn")
#                     return False

#             elif document.mime_type == "image/jpeg" and document.size == os.path.getsize(
#                 CONFIRM_AFTER_FIRST_IMG
#             ):
#                 print(f"{message.message.lower()} is not a bot image")
#                 return False
#         else:
#             return True

#     except Exception as e:
#         print(f"Error checking message history: {e}")
#         return False
