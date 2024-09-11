import asyncio
import html
import json
import logging
import textwrap

from aiogram import Bot, types, Dispatcher
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(level='INFO', format='[%(asctime)s] [%(levelname)-5s] %(message)s', datefmt='%d.%m.%Y %H:%M:%S')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter='__', extra='ignore')

    bot_token: str


settings = Settings()
bot = Bot(token=settings.bot_token)
dp = Dispatcher()


@dp.message()
async def default_message(message: types.Message):
    text = json.dumps(
        message.model_dump(mode='python', exclude_none=True),
        indent=4,
        ensure_ascii=False,
        default=lambda o: bot.default[o.name] if isinstance(o, Default) else str(o)
    )
    width_modifier = len(html.escape(text)) / len(text)
    text_chunks = textwrap.wrap(text, width=int(4000 // width_modifier), replace_whitespace=False)
    for text in text_chunks:
        await bot.send_message(
            message.chat.id,
            text=f"<pre>{html.escape(text)}</pre>",
            parse_mode=ParseMode.HTML
        )


async def start_bot():
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.exception(e)
            await asyncio.sleep(5)


asyncio.run(start_bot())
