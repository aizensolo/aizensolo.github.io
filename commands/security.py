from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import States

import dbworks

import texts
import variables

router = Router()

@router.message(Command("di"))
async def DebugInfo(message:Message, state:FSMContext):
    data = await state.get_data()
    mes = str(data)
    state_now = await state.get_state()
    mes += " " + str(state_now)
    await message.answer(mes if mes else "Nothing")

@router.message(Command("cancel"))
async def Cancel(message:Message, state:FSMContext):
    login_data = await state.get_data()

    if await state.get_state() in [States.logged_in, None]:
        await message.answer(texts.NOTHING_TO_CANCEL)
        return
    if login_data.get("password") == None:
        await state.set_state(None)
        await message.answer(texts.LOGIN_CANCEL)
        return
    await state.set_state(States.logged_in)
    await message.answer(texts.CANCEL)

@router.message(StateFilter(None), Command("login"))
async def OnLogin(message:Message, state:FSMContext):
    await message.answer(texts.LOGIN1)

    await state.set_state(States.loginning_username)

@router.message(States.loginning_username)
async def ProceedLoginning_NameStep(message:Message, state:FSMContext):
    login_data = await state.get_data()

    if not await dbworks.check_if_username_exists(message.text, variables.DATABASE_NAME):
        await message.answer(texts.LOGIN_NAME_ERR)
        return
        
    await state.update_data({"name":message.text})
    await state.set_state(States.loginning_password)
    await message.answer(texts.LOGIN2)

@router.message(States.loginning_password)
async def ProceedLoginning_PasswordStep(message:Message, state:FSMContext):
    login_data = await state.get_data()

    if not await dbworks.check_if_valid_password(login_data["name"], message.text, variables.DATABASE_NAME):
        await message.answer(texts.LOGIN_PASSWORD_ERR)
        return
    
    await state.update_data({"password":message.text})
    await state.set_state(States.logged_in)
    await message.answer(texts.LOGIN_SUCCESSFUL)

@router.message(States.logged_in, Command("logout"))
async def Logout(message:Message, state:FSMContext):
    await state.clear()
    await message.answer(texts.LOGOUT)