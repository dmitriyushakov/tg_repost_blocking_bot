from pyrogram import Client
from pyrogram.types import User
from typing import List, Callable, Optional
import logging
from command_analyzer import UserCommand
from configuration import get_configuration_instance

_logger = logging.getLogger(__name__)
configuration = get_configuration_instance()

async def block(client: Client, chat_id: int, _: User, args: List[str]):
    if len(args) != 1:
        await client.send_message(chat_id, "Block command receive one argument.")
    else:
        channel_name = args[0]
        await configuration.block(chat_id, channel_name)
        await client.send_message(chat_id, f"Channel {channel_name} is added to block list.")

async def unblock(client: Client, chat_id: int, _: User, args: List[str]):
    if len(args) != 1:
        await client.send_message(chat_id, "Unblock command receive one argument.")
    else:
        channel_name = args[0]
        await configuration.unblock(chat_id, channel_name)
        await client.send_message(chat_id, f"Channel {channel_name} is removed from block list.")

async def list_blocked(client: Client, chat_id: int, _: User, args: List[str]):
    if len(args) != 0:
        await client.send_message(chat_id, "List blocked command don't receive any arguments.")
    else:
        blocked_list = await configuration.list_blocked(chat_id)
        if len(blocked_list) == 0:
            await client.send_message(chat_id, "In this chat no one channel is blocked.")
        else:
            message = '\n'.join(["In this channel blocked"] + blocked_list)
            await client.send_message(chat_id, message)

async def list_granted(client: Client, chat_id: int, _: User, args: List[str]):
    if len(args) != 0:
        await client.send_message(chat_id, "List granted command don't receive any arguments.")
    else:
        users_in_chat = dict()
        async for member in client.get_chat_members(chat_id):
            member_user = member.user
            if member_user is None:
                continue
            users_in_chat[member_user.id] = member_user
        
        granted = await configuration.list_granted(chat_id)
        message = ["Granted users:"]

        for item in granted:
            if not item in granted:
                message.append(f"Left ({item})")
            else:
                user = users_in_chat[item]
                message.append(get_appeal(user, lambda user:f"Unknown ({user.id})"))
        
        await client.send_message(chat_id, '\n'.join(message))

async def find_user(client: Client, chat_id: int, keywords: List[str]) -> Optional[User]:
    if len(keywords) == 0:
        return None
    
    def remove_tag(keyword: str) -> str:
        if keyword.startswith('@'):
            return keyword[1:]
        else:
            return keyword
    
    keywords = list(map(remove_tag, keywords))

    async for member in client.get_chat_members(chat_id):
        user = member.user
        if user is None:
            continue

        user_keywords = set(kw for kw in (user.username, user.first_name, user.last_name) if not kw is None)
        if all(map(lambda kw:kw in user_keywords, keywords)):
            return user
    
    return None

async def grant(client: Client, chat_id: int, _: User, args: List[str]):
    if len(args) == 0:
        await client.send_message(chat_id, "Keywords requiered to find user")
    else:
        user_id = None
        try:
            if len(args) == 1:
                user_id = int(args[0])
        except ValueError:
            pass
        
        if not user_id is None:
            await configuration.grant(chat_id, user_id)
            await client.send_message(chat_id, f"User with id {user_id} is granted.")
            return
        
        user = await find_user(client, chat_id, args)
        
        if user is None:
            await client.send_message(chat_id, f"User \"{' '.join(args)}\" not found to grant.")
        else:
            await configuration.grant(chat_id, user.id)
            await client.send_message(chat_id, f"{get_appeal(user)} is granted.")

async def revoke(client: Client, chat_id: int, _: User, args: List[str]):
    if len(args) == 0:
        await client.send_message(chat_id, "Keywords requiered to find user")
    else:
        user_id = None
        try:
            if len(args) == 1:
                user_id = int(args[0])
        except ValueError:
            pass
        
        if not user_id is None:
            await configuration.revoke(chat_id, user_id)
            await client.send_message(chat_id, f"User with id {user_id} is revoked.")
            return
        
        user = await find_user(client, chat_id, args)
        
        if user is None:
            await client.send_message(chat_id, f"User \"{' '.join(args)}\" not found to revoke.")
        else:
            await configuration.revoke(chat_id, user.id)
            await client.send_message(chat_id, f"{get_appeal(user)} is revoked.")

async def respond_to_private_chat(client: Client, chat_id: int, user: User):
    message = f"""Hi, {get_appeal(user)}.
This bot remove reposts from channels which present in blacklist of your group chat.
Fell free add me to your chat and block unnecessary reposts."""
    
    await client.send_message(chat_id, message)

help_message = lambda user, bot_name:f"""Hi, {user}.
Let me describe, how you can configure me. You can ask me to change black lists or grants lists using by commands. Just tag me and print command with arguments after \"/\" char.
Below listed examples of supported commands:

{bot_name} /help - print this help
{bot_name} /block channel_name - add channel_name to blacklist
{bot_name} /unblock channel_name - remove channel_name from blacklist
{bot_name} /list_blocked - print blacklist contents
{bot_name} /grant user - add user to grants list. You can use username or first name and last name to chose user from chat. Granted users can edit black lists and grant lists.
{bot_name} /revoke user - remove user from grants list.
{bot_name} /list_granted - list granted users."""

async def help(client: Client, chat_id: int, user: User, args: List[str]):
    if len(args) != 0:
        await client.send_message("Help command expect no arguments.")
    else:
        user_appeal = get_appeal(user)
        bot_name = '@' + (client.me.username if not client.me is None else client.name)
        message = help_message(user_appeal, bot_name)
        await client.send_message(chat_id, message)

commands_table = {
    "block": block,
    "unblock": unblock,
    "list_blocked": list_blocked,
    "grant": grant,
    "revoke": revoke,
    "list_granted": list_granted,
    "help": help
}

def get_appeal(user: User, otherwise: Callable[[User], str] = lambda user: "USERNAME") -> str:
    if not user.username is None:
        return "@" + user.username
    elif not user.first_name is None:
        if not user.last_name is None:
            return f"{user.first_name} {user.last_name}"
        else:
            return user.first_name
    elif not user.last_name is None:
        return user.last_name
    else:
        return otherwise(user)

async def dispatch_command(client: Client, chat_id: int, user: User, command: UserCommand):
    user_id = user.id
    if not await  configuration.is_granted(chat_id, user_id):
        user_appeal = get_appeal(user)
        _logger.info(f"User {user_id} ({user_appeal}) tried to execute something in chat where is it not granted.\nCommand - {command}.")
        message = f"Sorry, {user_appeal}.\nYou are not granted to manage this bot."
        await client.send_message(chat_id, message)
    else:
        command_func = commands_table.get(command.command_name)
        if command_func is None:
            user_appeal = get_appeal(user)
            _logger.info(f"User {user_id} ({user_appeal}) tried to execute unknown command.\nCommand - {command}.")
            message = f"Sorry, {user_appeal}.\nCommand {command.command_name} is unknown."
            await client.send_message(chat_id, message)
        else:
            try:
                if _logger.level == logging.DEBUG:
                    user_appeal = get_appeal(user)
                    _logger.debug(f"User {user_id} ({user_appeal}) executing command - {command}.")
                await command_func(client, chat_id, user, command.args)
            except:
                user_appeal = get_appeal(user)
                _logger.exception(f"User {user_id} ({user_appeal}) tried to execute command but exception is happened.\nCommand - {command}.")
                message = f"Sorry, {user_appeal}.\nUnknown error happened during execution of your command :("
                await client.send_message(chat_id, message)