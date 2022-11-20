from client_provider import get_client_instance
from typing import Optional, List
import logging
import logging.config
import pyrogram
import logging
import yaml
import os, sys

_script_path = os.path.dirname(sys.argv[0])
_app_path = os.path.realpath(_script_path)
_configuration_filename = f"{_app_path}/configuration.yaml"
_logging_config_filename = f"{_app_path}/logging.yaml"
_logs_dir_filename = f"{_app_path}/logs"
_configuration_instance = None

_logger = logging.getLogger(__name__)

CHATS = "chats"
CHAT_ID = "id"
CHAT_BLOCKS = "blocks"
CHAT_GRANTS = "granted"

class Configuration:
    def __init__(self, config):
        self.config = config
        self._chat_entries = dict(map(lambda chat:(chat[CHAT_ID], chat), config[CHATS]))
    
    @staticmethod
    def load_configuration():
        configuration_file_contents = None
        try:
            with open(_configuration_filename, 'rt') as configuration_file:
                configuration_file_contents = yaml.load(configuration_file, yaml.Loader)
        except FileNotFoundError:
            _logger.warn(f"Configuration file \"{_configuration_filename}\" not found. New one will be created.")
            configuration_file_contents = {
                CHATS: []
            }
            with open(_configuration_filename, 'wt') as configuration_file:
                yaml.dump(configuration_file_contents, configuration_file)
        
        return Configuration(configuration_file_contents)
    
    async def _get_chat_entry(self, chat_id, detect_admins = True):
        if chat_id in self._chat_entries:
            return self._chat_entries[chat_id]
        else:
            new_chat_entry = {
                CHAT_ID: chat_id,
                CHAT_BLOCKS: [],
                CHAT_GRANTS: []
            }

            grants = new_chat_entry[CHAT_GRANTS]
            if detect_admins:
                tg_client = get_client_instance()
                async for member in tg_client.get_chat_members(chat_id, filter=pyrogram.enums.ChatMembersFilter.ADMINISTRATORS):
                    member_user = member.user
                    if member_user is None:
                        continue
                    grants.append(member_user.id)
            
            self.config[CHATS].append(new_chat_entry)
            self._chat_entries[chat_id] = new_chat_entry
            self.save_configuration()
            return new_chat_entry

    async def is_blocked(self, chat_id: int, channel_name: str):
        chat_entry = await self._get_chat_entry(chat_id)
        blocks = chat_entry[CHAT_BLOCKS]
        
        return channel_name in blocks
    
    async def block(self, chat_id: int, channel_name: str):
        chat_entry = await self._get_chat_entry(chat_id)
        blocks = chat_entry[CHAT_BLOCKS]
        
        if not channel_name in blocks:
            blocks.append(channel_name)
            self.save_configuration()
    
    async def unblock(self, chat_id: int, channel_name: str):
        chat_entry = await self._get_chat_entry(chat_id)
        blocks = chat_entry[CHAT_BLOCKS]
        
        if channel_name in blocks:
            blocks.remove(channel_name)
            self.save_configuration()

    async def list_blocked(self, chat_id) -> List[str]:
        chat_entry = await self._get_chat_entry(chat_id)
        return chat_entry[CHAT_BLOCKS]

    async def join_group(self, chat_id: int, admin_id: Optional[int]):
        chat_entry = await self._get_chat_entry(chat_id, admin_id is None)
        
        if not admin_id is None:
            grants = chat_entry[CHAT_GRANTS]
            if not admin_id in grants:
                grants.append(admin_id)
                self.save_configuration()

    async def is_granted(self, chat_id: int, user_id: int) -> bool:
        chat_entry = await self._get_chat_entry(chat_id)
        return user_id in chat_entry[CHAT_GRANTS]
    
    async def grant(self, chat_id: int, user_id: int):
        chat_entry = await self._get_chat_entry(chat_id)
        grants = chat_entry[CHAT_GRANTS]
        if not user_id in grants:
            grants.append(user_id)
            self.save_configuration()
    
    async def list_granted(self, chat_id: int) -> List[int]:
        chat_entry = await self._get_chat_entry(chat_id)
        return chat_entry[CHAT_GRANTS]
    
    async def revoke(self, chat_id: int, user_id: int):
        chat_entry = await self._get_chat_entry(chat_id)
        grants = chat_entry[CHAT_GRANTS]
        if user_id in grants:
            grants.remove(user_id)
            self.save_configuration()

    def save_configuration(self):
        with open(_configuration_filename, 'wt') as configuration_file:
            yaml.dump(self.config, configuration_file)

def get_configuration_instance() -> Configuration:
    global _configuration_instance
    if _configuration_instance is None:
        _configuration_instance = Configuration.load_configuration()
    return _configuration_instance

def configure_logging():
    try:
        try:
            if not os.path.isdir(_logs_dir_filename):
                os.mkdir(_logs_dir_filename)
        except:
            _logger.exception("Unable to create logs folder!")
        
        with open(_logging_config_filename, 'rt') as logging_config_file:
            logging_config = yaml.load(logging_config_file, yaml.Loader)
            logging.config.dictConfig(logging_config)
    except:
        logging.basicConfig(level = 'INFO')
        _logger.exception("Error during logging configuration loading occured. Fall back to basic config.")