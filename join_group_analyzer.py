from client_provider import get_client_instance
from pyrogram.types import ChatMemberUpdated
from collections import namedtuple
from typing import Optional

GroupJoin = namedtuple("GroupJoin", ["chat_id", "admin_id", "admin_username", "admin_first_name", "admin_last_name"])

def analyze_join(update: ChatMemberUpdated) -> Optional[GroupJoin]:
    chat_id = update.chat.id

    if not update.old_chat_member is None:
        return None
    
    if update.new_chat_member is None:
        return None
    
    member_user = update.new_chat_member.user
    if member_user is None:
        return None
    
    member_user_id = member_user.id
    
    client = get_client_instance()
    client_me = client.me
    if client_me is None:
        return None
    
    client_me_id = client_me.id

    if member_user_id != client_me_id:
        return None
    
    invited_by = update.new_chat_member.invited_by
    invited_by_id = None
    invited_by_username = None
    invited_by_first_name = None
    invited_by_last_name = None

    if not invited_by is None:
        invited_by_id = invited_by.id
        invited_by_username = invited_by.username
        invited_by_first_name = invited_by.first_name
        invited_by_last_name = invited_by.last_name
    
    return GroupJoin(
        chat_id = chat_id,
        admin_id = invited_by_id,
        admin_username = invited_by_username,
        admin_first_name = invited_by_first_name,
        admin_last_name = invited_by_last_name
    )