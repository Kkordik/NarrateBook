from services.token import TokenService
from services.user import UserService
from services.oauth_client import OAuthClientService
from services.oauth_code import OAuthCodeService
from database.init_session import async_session
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()  # Load environment variables

# Pyrogram client setup
app = Client(
    "my_bot",
    api_id=os.getenv('TELEGRAM_API_ID'),
    api_hash=os.getenv('TELEGRAM_API_HASH'),
    bot_token=os.getenv('TELEGRAM_BOT_TOKEN')
)

token_service = TokenService(async_session)
user_service = UserService(async_session)
oauth_cli_service = OAuthClientService(async_session)
oauth_code_service = OAuthCodeService()


def get_command_data(command_params: str):
    key_list = ['state', 'client_id']
    params_list = [None if x == 'None' else x for x in command_params.split('_')]
    if len(key_list) == len(params_list):
        data = dict(zip(key_list, params_list))
        return data
    return None


@app.on_message(filters.command("start"))
async def start_command(_, message):
    await user_service.add_user(message.from_user.id)

    if len(message.command) > 1:
        data = get_command_data(message.text.removeprefix(message.command[0]+' '))
        state = f"&state={data['state']}" if data["state"] else ""
        client_id = data["client_id"]

        auth_code_str = await oauth_code_service.create_auth_code(message.from_user.id)
        redirect_uri = await oauth_cli_service.get_redirect_uri(client_id)
        if not redirect_uri:
            await message.reply("Hello! This is an auth bot for narratebook.com")
            return

        url = f"{redirect_uri}?code={auth_code_str}{state}"

        reply_msg = await message.reply(
            "Approve access and continue, press the inline button below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Authorize", url=url)]])
        )
        await asyncio.sleep(60*int(os.getenv('CODE_EXPIRE_MIN')))
        await reply_msg.edit_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("Expired", callback_data='expired')]]))
    else:
        await message.reply("Hello! This is an auth bot for narratebook.com")

app.run()  # Run the bot
