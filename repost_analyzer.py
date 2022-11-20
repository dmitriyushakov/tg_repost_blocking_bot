from pyrogram.types import Message
from collections import namedtuple
from typing import Optional
import logging

_logger = logging.getLogger(__name__)
Repost = namedtuple("Repost", ["id", "chat_id", "channel_name"])

def analyze_repost(message: Message) -> Optional[Repost]:
    if _logger.level == logging.DEBUG and not message.forward_from_chat is None:
        _logger.debug(f"Forwarded message detected:\n{message}")
    
    id = message.id
    
    chat = message.chat
    if chat is None:
        return None
    
    chat_id = chat.id

    forward_from_chat = message.forward_from_chat
    if forward_from_chat is None:
        return None
    
    forward_from_chat_username = forward_from_chat.username

    repost_data =  Repost(
        id = id,
        chat_id = chat_id,
        channel_name = forward_from_chat_username
    )

    _logger.info(f"Repost - {repost_data}")

    return repost_data