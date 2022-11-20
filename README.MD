# Telegram repost blocking bot
This bot allow to remove reposts in channels which are present in black list.

## Quick start guide
1. Clone repository, install modules and try to start application.
```bash
git clone https://github.com/dmitriyushakov/tg_repost_blocking_bot.git
cd tg_repost_blocking_bot
pipenv install
pipenv shell
python bot.py
```
2. After first start ```secrets.yaml``` file will be generated:
```yaml
api_hash: ''
api_id: 0
bot_account: ''
bot_token: ''
```
Fill bot credentials. ```api_hash``` and ```api_id``` which required for MTProto client you can get [from my.telegram.org](https://core.telegram.org/api/obtaining_api_id). ```bot_token``` you can get [from @BotFather](https://core.telegram.org/bots#how-do-i-create-a-bot). ```bot_account``` should be same as username provided to @BotFather.

3. After fill ```secrets.yaml``` you can start application again. Make sure that pipenv environment still activated:
```bash
python bot.py
```

## Commands
Configuration of blacklists can be finished manually by edit of ```configuration.yaml``` or in chat where bot were added. Mention bot by his username and fill command after "/" char. You can get help about commands by "help" command in group chat where it were added:
```
@YourBotAccountName /help
```