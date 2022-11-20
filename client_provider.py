from pyrogram import Client
from typing import Optional
import yaml
import os, sys
import logging

_script_path = os.path.dirname(sys.argv[0])
_app_path = os.path.realpath(_script_path)
_secrets_filename = f"{_app_path}/secrets.yaml"
_logger = logging.getLogger(__name__)
_client_instance = None
_client_instance_initialized = False

BOT_ACCOUNT = "bot_account"
API_ID = "api_id"
API_HASH = "api_hash"
BOT_TOKEN = "bot_token"

def validate_tg_secrets(secrets) -> bool:
    if not type(secrets) is dict:
        _logger.error("Unknow type of object received. Validation of screts failed.")
        return False
    
    keys_to_check = [
        (BOT_ACCOUNT, str, ""),
        (API_ID, int, 0),
        (API_HASH, str, ""),
        (BOT_TOKEN, str, "")
    ]

    validation_success = True
    for key, key_type, default_value in keys_to_check:
        if not key in secrets:
            _logger.error(f"Entry with \"{key}\" key not exists in secrets config.")
            validation_success = False
        else:
            value = secrets[key]
            if not type(value) is key_type:
                _logger.error(f"Entry with \"{key}\" key in secrets config is not \"{key_type.__name__}\" type.")
                validation_success = False
            elif value == default_value:
                _logger.error(f"Entry with \"{key}\" key in secrets config is empty value.")
                validation_success = False
    
    if not validation_success:
        _logger.error("Validation failed.")
    
    return validation_success

def load_tg_secrets() -> Optional[dict]:
    secrets_file_contents = None
    
    try:
        with open(_secrets_filename, 'rt') as secrets_file:
            secrets_file_contents = yaml.load(secrets_file, yaml.Loader)
            if not validate_tg_secrets(secrets_file_contents):
                return None
    except FileNotFoundError:
        _logger.warn(f"Secrets \"{_secrets_filename}\" not exists. New one will be created!")
        secrets_file_contents = {
            BOT_ACCOUNT: "",
            API_ID: 0,
            API_HASH: "",
            BOT_TOKEN: ""
        }
        with open(_secrets_filename, 'wt') as secrets_file:
            yaml.dump(secrets_file_contents, secrets_file)
        
        _logger.warn(f"New secrets file created by path \"{_secrets_filename}\". Please fill your bot credentials here.")
        return None
    
    return secrets_file_contents

def create_tg_client() -> Optional[Client]:
    secrets = load_tg_secrets()

    if secrets is None:
        _logger.error("Failed to load secrets file. Unable to create Telegram client instance.")
        return None
    else:
        app = Client(
            name = secrets[BOT_ACCOUNT],
            api_id = secrets[API_ID],
            api_hash = secrets[API_HASH],
            bot_token = secrets[BOT_TOKEN]
        )

        return app

def get_client_instance() -> Optional[Client]:
    global _client_instance
    global _client_instance_initialized

    if _client_instance_initialized:
        return _client_instance
    else:
        _client_instance = create_tg_client()
        _client_instance_initialized = True
        return _client_instance