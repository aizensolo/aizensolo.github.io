from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter

import texts

router = Router()

@router.message(CommandStart())
async def OnStart(message:Message):
    await message.answer(texts.ONSTART)

@router.message(StateFilter(None), Command("help"))
async def OnHelp(message:Message):
    await message.answer(texts.ONHELP_NOT_LOGGED_IN)