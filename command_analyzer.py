import logging
from typing import Optional
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from collections import namedtuple
from client_provider import get_client_instance

_logger = logging.getLogger(__name__)

UserCommand = namedtuple("UserCommand", ["chat_id", "command_name", "args"])

def get_mentions_list(message: Message):
    mentions_list = list()
    if message.entities is None:
        return mentions_list
    
    text = message.text
    for entity in message.entities:
        if entity.type == MessageEntityType.MENTION:
            begin_pos = entity.offset + 1
            end_pos = entity.offset + entity.length
            mentions_list.append(text[begin_pos:end_pos])
    
    return mentions_list

def parse_command(chat_id: int, command_line:str) -> Optional[UserCommand]:
    slash_idx = command_line.find('/')
    
    if slash_idx == -1:
        return None
    else:
        command_line = command_line[slash_idx+1:]
        line_iter = iter(command_line)
        parts = list()
        arg = list()

        for ch in line_iter:
            arg.clear()
            if ch == ' ':
                continue
            elif ch == "'":
                for ch in line_iter:
                    if ch == "'":
                        parts.append(''.join(arg))
                        arg.clear()
                        break
                    else:
                        arg.append(ch)
            elif ch == '"':
                escape = False
                for ch in line_iter:
                    if escape:
                        arg.append(ch)
                        escape = False
                    else:
                        if ch == "\\":
                            escape = True
                        elif ch == "\"":
                            parts.append(''.join(arg))
                            arg.clear()
                            break
                        else:
                            arg.append(ch)
            else:
                arg.append(ch)
                for ch in line_iter:
                    if ch == ' ':
                        parts.append(''.join(arg))
                        arg.clear()
                        break
                    else:
                        arg.append(ch)
            
        if len(arg) > 0:
            parts.append(''.join(arg))
        
        if len(parts) == 0:
            return None
        else:
            command_name = parts[0]
            args = parts[1:]

            return UserCommand(chat_id, command_name, args)

def me_mentioned(message: Message) -> bool:
    client = get_client_instance()
    username = None
    client_me = client.me
    if not client_me is None:
        username = client_me.username
    else:
        username = client.name

    mentions = get_mentions_list(message)
    
    return username in mentions

def parse_command_in_message(message: Message) -> Optional[UserCommand]:
    if me_mentioned(message):
        chat_id = message.chat.id
        message_text = message.text
        command = parse_command(chat_id, message_text)

        if command is None:
            _logger.warn(f"Unable to parse command in chat {chat_id} - {message_text}")
        else:
            _logger.info(f"Parsed command - {command}\nText - {message_text}")
        
        return command