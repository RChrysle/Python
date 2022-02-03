from datetime import datetime, timedelta
from pyrogram import Client, filters
from bot import user_time
from config import youtube_next_fetch
from helper.ytdlfunc import extractYt, create_buttons
import wget
import os
from pyrogram.types import InlineKeyboardButton , InlineKeyboardMarkup
from PIL import Image
from aiogram import executor
from aiogram import Dispatcher
from aiogram import Bot
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup , KeyboardButton
from typing import Union
from pytube import YouTube
import time


ytregex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
BOT_TOKEN = "5025795879:AAE18DGSkEEcARNDlg7oAjJ23PffYBKxw00"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
kanal = ['https://t.me/pythonking01']

async def check(user_id , kanal : Union[str , int]):
    bot2 = Bot.get_current()
    subrc = await bot2.get_chat_member(user_id=user_id , chat_id=kanal)
    return subrc.is_chat_member()
@dp.message_handler(commands='start')
async def starter(request:types.Message):
    name = request.from_user
    await request.reply(text=f'Hi {name.first_name} . Welcome to Youtube World ' , reply_markup=btn)
btn = ReplyKeyboardMarkup(
    keyboard= [
        [
            KeyboardButton(text="Youtube Videos Search"),
        ],



        [
            KeyboardButton(text="Gif Search")
        ],


    ]
)

@dp.message_handler(text='Youtube Videos Search')
async def help(message: types.Message):
    await message.answer(text='To search for a video, type the name of the video you are looking for next to @vid in the message field.'
                              ' Then click the send button to send')

@dp.message_handler(text='Gif Search')
async def gif(messages: types.Message):
    await messages.answer(text='To search for a video, type the name of the video you are looking for next to @gif in the message field.'
                              ' Then click the send button to send')


@Client.on_message(filters.regex(ytregex))
async def ytdl(_, message):
    userLastDownloadTime = user_time.get(message.chat.id)
    try:
        if userLastDownloadTime > datetime.now():
            wait_time = round((userLastDownloadTime - datetime.now()).total_seconds() / 60, 2)
            await message.reply_text(f"`Wait {wait_time} Minutes before next Request`")
            return
    except:
        pass

    url = message.text.strip()
    await message.reply_chat_action("typing")
    try:
        title, thumbnail_url, formats = extractYt(url)

        now = datetime.now()
        user_time[message.chat.id] = now + \
                                     timedelta(minutes=youtube_next_fetch)

    except Exception:
        await message.reply_text("`Failed To Fetch Youtube Data... 😔 \nPossible Youtube Blocked server ip \n#error`")
        return
    buttons = InlineKeyboardMarkup(list(create_buttons(formats)))
    sentm = await message.reply_text("Processing Youtube Url 🔎 🔎 🔎")
    try:
        # Todo add webp image support in thumbnail by default not supported by pyrogram
        # https://www.youtube.com/watch?v=lTTajzrSkCw
        img = wget.download(thumbnail_url)
        im = Image.open(img).convert("RGB")
        output_directory = os.path.join(os.getcwd(), "downloads", str(message.chat.id))
        if not os.path.isdir(output_directory):
            os.makedirs(output_directory)
        thumb_image_path = f"{output_directory}.jpg"
        im.save(thumb_image_path,"jpeg")
        await message.reply_photo(thumb_image_path, caption=title, reply_markup=buttons)
        await sentm.delete()
    except Exception as e:
        print(e)
        try:
            thumbnail_url = "https://telegra.ph/file/ce37f8203e1903feed544.png"
            await message.reply_photo(thumbnail_url, caption=title, reply_markup=buttons)
        except Exception as e:
            await sentm.edit(
            f"<code>{e}</code> #Error")
if __name__ == '__main__':
    executor.start_polling(dp , skip_updates=True)
