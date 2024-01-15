from models.token import TokenModel
from models.user import UserModel
from models.oauth_client import OAuthClientModel
from models.oauth_code import OAuthCodeModel
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


def get_command_data(command_params: str):
    print(command_params)
    key_list = ['state', 'client_id']
    params_list = [None if x == 'None' else x for x in command_params.split('_')]
    if len(key_list) == len(params_list):
        data = dict(zip(key_list, params_list))
        return data
    return None


@app.on_message(filters.command("start"))
async def start_command(_, message):
    await UserModel(async_session).add_user(message.from_user.id)

    if len(message.command) > 1:
        data = get_command_data(message.text.split()[1])
        state = f"&state={data['state']}" if data["state"] else ""
        client_id = data["client_id"]

        auth_code_str = await OAuthCodeModel(async_session, user_id=message.from_user.id).create_auth_code()
        redirect_uri = await OAuthClientModel(async_session).get_redirect_uri(client_id)
        if not redirect_uri:
            await message.reply("Hello! This is an auth bot for narratebook.com")
            return

        url = f"{redirect_uri}?code={auth_code_str}{state}"
        print("the url ", url)
        reply_msg = await message.reply(
            "Approve access and continue, press the inline button below:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Authorize", url=url)]])
        )
        await asyncio.sleep(60*int(os.getenv('CODE_EXPIRE_MIN')))
        await reply_msg.edit_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("Expired", callback_data='expired')]]))
    else:
        await message.reply("Hello! This is an auth bot for narratebook.com")

app.run()  # Run the bot
