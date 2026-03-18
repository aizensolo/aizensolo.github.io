from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import States

import dbworks
import texts
import variables

router = Router()

@router.message(States.logged_in, Command("leaderboard"))
async def GetLeaderboards(message:Message, state:FSMContext):
    leaderboards = await dbworks.get_top_by_money(variables.DATABASE_NAME)
    text = ""

    for row in leaderboards:
        text += f"<b>{row[0]}</b> | <b>{row[1]}</b>\n"

    await message.answer(text, parse_mode="html")

@router.message(States.logged_in, Command("help"))
async def OnHelp(message:Message):
    await message.answer(texts.ONHELP, parse_mode="html")

@router.message(States.logged_in, Command(commands=["me", "balance"]))
async def CheckBalance(message:Message, state:FSMContext):
    account_info = await state.get_data()

    result = await dbworks.check_balance(account_info["name"], account_info["password"], variables.DATABASE_NAME)

    if result >= 0:
        await message.answer(texts.BALANCE + str(result))
        return
    await message.answer(texts.BALANCE_ERROR)

@router.message(States.logged_in, Command("transfer"))
async def TransferMoney(message:Message, state:FSMContext):
    await state.set_state(States.transfering_name)
    await message.answer(texts.TRANSFER_ENTER_NAME)

@router.message(States.transfering_name)
async def EnterNameToProceed(message:Message, state:FSMContext):
    account_data = await state.get_data()

    if account_data["name"] == message.text:
        await message.answer(texts.TRANSFER_SAME_NAME_ERROR)
        return
    if await dbworks.check_if_username_exists(message.text, variables.DATABASE_NAME):
        await state.update_data({"transfering_to":message.text})
        await state.set_state(States.transfering_value)
        await message.answer(texts.TRANSFER_ENTER_VALUE)
        return
    await message.answer(texts.TRANSFER_NAME_ERROR)

@router.message(States.transfering_value)
async def EnterValueToProceed(message:Message, state:FSMContext):
    value = 0

    try:
        value = float(message.text)
    except:
        await message.answer(texts.TRANSFER_INVALID_VALUE_ERROR)
        return
    
    if value <= 0:
        await message.answer(texts.TRANSFER_VALUE_BELOW_ERROR)
        return
    
    account_info = await state.get_data()
    
    if await dbworks.check_balance(account_info["name"], account_info["password"], variables.DATABASE_NAME) >= value:
        await state.update_data({"transfering_value":value})

        buttons = [
            [InlineKeyboardButton(text=texts.COMMENT_YES, callback_data="add-comment")],
            [InlineKeyboardButton(text=texts.COMMENT_NO, callback_data="deny-comment")]
        ]

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(texts.TRANSFER_COMMENT_OR_NOT, reply_markup=kb)
        return
    await message.answer(texts.TRANSFER_VALUE_NOT_ENOUGH_ERROR)

@router.callback_query(States.logged_in, Command("get_operations"))
async def GetOperations(message:Message, state:FSMContext):
    await message.answer(texts.IN_REWORK)

@router.callback_query(States.transfering_value, F.data == "add-comment")
async def AddCommentToOperation(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    await state.set_state(States.transfering_comment)
    await callback.message.answer(texts.COMMENT_ENTER)

async def OperationConfirmation(message:Message, state:FSMContext):
    buttons = [
        [InlineKeyboardButton(text=texts.TRANSFER_ALRIGHT, callback_data="transfer-confirm")],
        [InlineKeyboardButton(text=texts.TRANSFER_NOT_ALRIGHT, callback_data="transfer-deny")]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    info = await state.get_data()

    comment = info.get("transfering_comment")
    transfer_text = f"{texts.TRANSFER_ALL_ALRIGHT}\n\n{texts.RECIPIENT}{info["transfering_to"]}\n{texts.VALUE}{info["transfering_value"]}\n{texts.COMMENT + comment if comment else ''}"

    await message.answer(transfer_text, reply_markup=kb)

@router.callback_query(F.data == "transfer-confirm")
async def OperationExceution(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    data = await state.get_data()

    sender_name = data["name"]
    sender_password = data["password"]
    value = data["transfering_value"]
    recipient_name = data["transfering_to"]
    comment = data.get("transfering_comment")

    if await dbworks.transfer(sender_name, sender_password, value, recipient_name, variables.DATABASE_NAME):
        await state.set_data({"name":sender_name, "password":sender_password})
        await state.set_state(States.logged_in)
        await callback.message.answer(texts.TRANSFER_FINISHED)
        return
    await callback.message.answer(texts.TRANSFER_ERROR)

@router.callback_query(F.data == "transfer-deny")
async def TransferDeny(callback:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    new_data = {"name":data["name"], "password":data["password"]}
    await state.set_data(new_data)
    await state.set_state(States.logged_in)
    await callback.message.delete()
    await callback.message.answer(texts.TRANSFER_DENIED)

@router.callback_query(States.transfering_value, F.data == "deny-comment")
async def ProceedWithoutComment(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()

    await OperationConfirmation(callback.message, state)

@router.message(States.transfering_comment)
async def ConfirmOperation(message:Message, state:FSMContext):
    await state.update_data({"transfering_comment":message.text})

    await OperationConfirmation(message, state)