from pyrogram import Client
from pyrogram.errors.exceptions.forbidden_403 import MessageDeleteForbidden
from pyrogram.handlers import MessageHandler
from pyrogram.handlers import ChatMemberUpdatedHandler
from pyrogram.types import Message
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatType
from configuration import get_configuration_instance, configure_logging
from client_provider import get_client_instance
from repost_analyzer import analyze_repost
from command_analyzer import me_mentioned, parse_command_in_message
from commands import dispatch_command, get_appeal, respond_to_private_chat, help
from join_group_analyzer import analyze_join, GroupJoin
import logging

_logger = logging.getLogger(__name__)

def is_private_chat_message(message: Message) -> bool:
    return bool(message.chat and message.chat.type in {ChatType.PRIVATE, ChatType.BOT})

async def process_message(client: Client, message: Message):
    if is_private_chat_message(message):
        await respond_to_private_chat(client, message.chat.id, message.from_user)
        return
    
    config = get_configuration_instance()
    repost = analyze_repost(message)

    if not repost is None:
        if await config.is_blocked(repost.chat_id, repost.channel_name):
            _logger.info(f"Received repost message to block - {repost}")
            try:
                await client.delete_messages(repost.chat_id, repost.id)
            except MessageDeleteForbidden:
                _logger.error(f"Message deletion forbidden in chat with id {repost.chat_id}")
                msg = f"Unfortunately message deletion forbidden for me :(\nI'm unable to delete message from {repost.channel_name}!"
                await client.send_message(repost.chat_id, msg)
    
    if me_mentioned(message):
        user = message.from_user
        if user is None:
            return
        user_id = user.id
        chat_id = message.chat.id
        
        user_command = parse_command_in_message(message)
        if user_command is None:
            user_appeal = get_appeal(user)
            _logger.info(f"User {user_id} ({user_appeal}) sent command which not parsed.")
            message = f"Sorry, {user_appeal}.\nI don't understand your command."
            await client.send_message(chat_id, message)
        else:
            await dispatch_command(client, chat_id, user, user_command)


def get_greetings_line(join: GroupJoin) -> str:
    line = "Hi, "

    if not join.admin_username is None:
        line += "@" + join.admin_username
    elif not join.admin_first_name is None:
        line += join.admin_first_name
        if not join.admin_last_name is None:
            line += " " + join.admin_last_name
    elif not join.admin_last_name is None:
        line += join.admin_last_name
    else:
        line += "USERNAME"
    
    return line

async def handle_chat_member_updated(client: Client, update: ChatMemberUpdated):
    config = get_configuration_instance()
    join = analyze_join(update)
    if not join is None:
        await config.join_group(join.chat_id, join.admin_id)
        greetings_message = get_greetings_line(join) + "\nLet me remove reposts from hostile channels!\nFirst of all don't forget to grant me permissions to delete messages."
        await client.send_message(join.chat_id, greetings_message)
        await help(client, update.chat.id, update.from_user, [])

def run_application():
    app = get_client_instance()
    if app is None:
        _logger.error("Telegram client is not created. Application will not be started.")
    else:
        app.add_handler(MessageHandler(process_message))
        app.add_handler(ChatMemberUpdatedHandler(handle_chat_member_updated))
        app.run()

if __name__ == '__main__':
    configure_logging()
    run_application()