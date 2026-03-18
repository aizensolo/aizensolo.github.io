from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import States

import dbworks
import texts
import variables

import specutils

router = Router()

@router.message(States.logged_in, Command("manage_trades"))
async def ManageTradeMenu(message:Message, state:FSMContext):
    account_info = await state.get_data()
    trade_ids = await dbworks.get_trade_ids_by_user(account_info["name"], variables.DATABASE_NAME)
    if not trade_ids:
        await message.answer(texts.MANAGE_TRADES_NO_TRADE_IDS)
        return
    # buttons = [InlineKeyboardButton(text=trade_id[0], callback_data=f"mt-{trade_id[0]}") for trade_id in trade_ids] 
    # buttons = [[InlineKeyboardButton(text=trade_id[i][0], callback_data=f"mt-{trade_id[i][0]}") for trade_id in range(i)] for i in range(len(trade_ids))]
    buttons = [[InlineKeyboardButton(text=trade_ids[i*2+it][0], callback_data=f"mt-{trade_ids[i*2+it][0]}") for it in range(2)] for i in range(int(len(trade_ids)/2))]
    if len(buttons)*2 < len(trade_ids):
        buttons.append([InlineKeyboardButton(text=trade_ids[len(trade_ids)-1][0], callback_data=f"mt-{trade_ids[len(trade_ids)-1][0]}")])
    buttons.append([InlineKeyboardButton(text=texts.MANAGE_TRADES_CANCEL_CHOOSE, callback_data="manage-t-cancel-choose")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(States.trades_managment)

    await message.answer(texts.MANAGE_TRADES_CHOOSE, reply_markup=kb)

@router.callback_query(States.trades_managment, F.data == "manage-t-cancel-choose")
async def ManageTradeChooseCancel(callback:CallbackQuery, states:FSMContext):
    await callback.message.delete()
    await states.set_state(States.logged_in)

@router.callback_query(States.trades_managment, F.data.startswith('mt-'))
async def ManageTrade(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    trade_id = callback.data.split('-')[1]
    _, cost = await dbworks.search_trade_id(trade_id, variables.DATABASE_NAME)

    text = f"{texts.COST}{cost}\n\n{texts.MANAGE_TRADES_WHAT_TO_DO}"

    await state.update_data({"mt":trade_id})

    buttons = [
        [InlineKeyboardButton(text=texts.MANAGE_TRADES_DELETE, callback_data="manage-trade-delete")],
        [InlineKeyboardButton(text=texts.MANAGE_TRADES_CHANGE, callback_data="manage-trade-change")],
        [InlineKeyboardButton(text=texts.MANAGE_TRADES_NOTHING, callback_data="manage-trade-cancel")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer(text, reply_markup=kb)

@router.callback_query(States.trades_managment, F.data == "manage-trade-cancel")
async def CancelManaginTrades(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    await state.set_state(States.logged_in)
    data = await state.get_data()
    await state.set_data({"name":data["name"], "password":data["password"]})

@router.callback_query(States.trades_managment, F.data == "manage-trade-change")
async def ManageTradeEdit(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    await state.set_state(States.logged_in)
    data = await state.get_data()
    await state.set_data({"name":data["name"], "password":data["password"]})

    await callback.message.answer(texts.MTD_INDEV)

@router.callback_query(States.trades_managment, F.data == "manage-trade-delete")
async def ManageTradeDelete(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    await state.set_state(States.deleting_trade)
    await callback.message.answer(texts.MANAGE_TRADE_DELETE)

@router.message(States.deleting_trade, F.data == texts.MTD_YES)
async def TradeDelete(message:Message, state:FSMContext):
    data = await state.get_data()

    await state.set_state(States.logged_in)
    await state.set_state({"name":data["name"], "password":data["password"]})

    if await dbworks.delete_trade_id(data["name"], data["password"], data["mt"], variables.DATABASE_NAME):
        await message.answer(texts.MTD_SUCCESS)
        return
    await message.answer(texts.MTD_ERROR)

@router.message(States.deleting_trade)
async def TradeDeleteCancel(message:Message, state:FSMContext):
    data = await state.get_data()
    await state.set_state(States.logged_in)
    await state.set_data({"name":data["name"], "password":data["password"]})

    await message.answer(texts.MTD_CANCEL)

@router.message(States.logged_in, Command("pay"))
async def EnterPayID(message:Message, state:FSMContext):
    await state.set_state(States.entering_pay_id)
    await message.answer(texts.PAY)

@router.message(States.entering_pay_id)
async def PayConfirmation(message:Message, state:FSMContext):
    if await dbworks.is_trade_id_avaliable(message.text, variables.DATABASE_NAME):
        await message.answer(texts.PAY_NO_TRADE_ID)
        return
    
    name, value = await dbworks.search_trade_id(message.text, variables.DATABASE_NAME)
    account_info = await state.get_data()

    if await dbworks.check_balance(account_info["name"], account_info["password"], variables.DATABASE_NAME) < value:
        await message.answer(texts.TRANSFER_VALUE_NOT_ENOUGH_ERROR)
        await state.set_state(States.logged_in)
        return

    await state.update_data({"paydata":{"name":name, "value":value, "id":message.text}})

    buttons = [
        [InlineKeyboardButton(text=texts.PAY_YES, callback_data="pay")],
        [InlineKeyboardButton(text=texts.PAY_NO, callback_data="pay-cancel")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"{texts.PAY_INFO}\n\n{texts.COST}{value}\n{texts.RECIPIENT}{name}"
    await message.answer(text, reply_markup=kb)

@router.callback_query(States.entering_pay_id, F.data == "pay")
async def Pay(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    await state.set_state(States.logged_in)
    if await dbworks.transfer(data["name"], data["password"], data["paydata"]["value"], data["paydata"]["name"], variables.DATABASE_NAME):
        await state.set_data({"name":data["name"], "password":data["password"]})
        await callback.message.answer(texts.TRANSFER_FINISHED)
        return
    await state.set_data({"name":data["name"], "password":data["password"]})
    await callback.message.answer(texts.TRANSFER_ERROR)

@router.callback_query(States.entering_pay_id, F.data == "pay-cancel")
async def CancelPay(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    await state.set_data({"name":data["name"], "password":data["password"]})
    await state.set_state(States.logged_in)

@router.message(States.entering_trade_id, Command("tradepack"))
@router.message(States.logged_in, Command("tradepack"))
async def AboutTradePack(message:Message):
    await message.answer(texts.TRADEPACK_DESC)

@router.message(States.entering_trade_id, Command("buytradepack"))
@router.message(States.logged_in, Command("buytradepack"))
async def BuyTradePack(message:Message, state:FSMContext):
    account_data = await state.get_data()

    if await dbworks.is_tradepack_bought(account_data["name"], variables.DATABASE_NAME):
        await message.answer(texts.TRADEPACK_ALREADY_BOUGHT)
        return
    
    await state.set_state(States.buying_tradepack)

    buttons = [
        [InlineKeyboardButton(text=texts.TRADE_CONTINIUE_REGISTERING, callback_data="buytp-continiue")],
        [InlineKeyboardButton(text=texts.TRADE_CANCEL_REGISTERING, callback_data="buytp-cancel")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(texts.BUY_TRADEPACK, reply_markup=kb)

@router.callback_query(States.buying_tradepack, F.data == "buytp-continiue")
async def BuyingTradePack(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    account_info = await state.get_data()

    await state.set_state(States.logged_in)
    if await dbworks.check_balance(account_info["name"], account_info["password"], variables.DATABASE_NAME) >= 210:
        if await dbworks.buy_tradepack(account_info["name"], account_info["password"], 210, variables.DATABASE_NAME):
            await callback.message.answer(texts.THANKS_FOR_BUYING_TRADEPACK)
            return
        await callback.message.answer(texts.BUY_TRADEPACK_ERROR)
        return
    await callback.message.answer()

@router.callback_query(States.buying_tradepack, F.data == "buytp-cancel")
async def CancelBuyingTradePack(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    await state.set_state(States.logged_in)
    await callback.message.answer(texts.BUY_TRADEPACK_CANCEL)

@router.message(States.entering_trade_id, Command("help_trade"))
@router.message(States.logged_in, Command("help_trade"))
async def AboutTradeSystem(message:Message):
    await message.answer(texts.ABOUT_TRADE_ID)

@router.message(States.logged_in, Command("trade_id"))
async def CreateTradeId(message:Message, state:FSMContext):
    account_info = await state.get_data()

    if await dbworks.is_tradepack_bought(account_info["name"], variables.DATABASE_NAME):
        if await dbworks.how_much_trade_ids_on_user(account_info["name"], variables.DATABASE_NAME) > 9:
            await message.answer(texts.TRADE_ID_LIMIT_REACHED)
            return
    else:
        if await dbworks.how_much_trade_ids_on_user(account_info["name"], variables.DATABASE_NAME) > 2:
            await message.answer(texts.TRADE_ID_LIMIT_REACHED_FREE)
            return

    await state.set_state(States.entering_trade_id)
    await message.answer(texts.ONTRADE_ID)

@router.message(States.entering_trade_id)
async def CheckTradeIDAvaliable(message:Message, state:FSMContext):
    if not await specutils.check_trade_id_is_correct(message.text):
        await message.answer(texts.TRADE_ID_HAVE_SPECIAL_SYMBOLS)
        return
    if not await dbworks.is_trade_id_avaliable(message.text, variables.DATABASE_NAME):
        await message.answer(texts.TRADE_ID_ALREADY_HANDLED_ERROR)
        return
    
    await state.update_data({"registering_trade_id":message.text})
    
    buttons = [
        [InlineKeyboardButton(text=texts.TRADE_CONTINIUE_REGISTERING, callback_data="registering-continiue")],
        [InlineKeyboardButton(text=texts.TRADE_CANCEL_REGISTERING, callback_data="registering-cancel")]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(texts.TRADE_ID_NOT_HANDLED, reply_markup=kb)

@router.message(States.entering_trade_value)
async def EnterValueForTradeID(message:Message, state:FSMContext):
    value = 0

    try:
        value = float(message.text)
    except:
        await message.answer(texts.TRADE_REGISTER_VALUE_ERROR)
        return
    
    data = await state.get_data()
    
    await state.update_data({"registering_trade_value":value})

    buttons = [
        [InlineKeyboardButton(text=texts.TRADE_CONTINIUE_REGISTERING, callback_data="register-trade-id")],
        [InlineKeyboardButton(text=texts.TRADE_CANCEL_REGISTERING, callback_data="cancel-register-trade-id")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    text = f"{texts.TRADE_WANT_TO_CONTINIUE}\n\n{texts.COST}: {value}\n{texts.RECIPIENT}: {data["name"]}"

    await message.answer(text, reply_markup=kb)

@router.callback_query(States.entering_trade_value, F.data == "register-trade-id")
async def RegisterTradeID(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    data = await state.get_data()

    await state.set_data({"name":data["name"], "password":data["password"]})
    await state.set_state(States.logged_in)

    if await dbworks.create_trade_id(data["registering_trade_id"], data["name"], data["password"], data["registering_trade_value"], variables.DATABASE_NAME):
        await callback.message.answer(texts.TRADE_ID_SUCCESSFULLY_CREATED)
        return
    await callback.message.answer(texts.TRADE_ID_ERROR)

@router.callback_query(States.entering_trade_id, F.data == "registering-continiue")
async def ContiniueRegisteringTradeID(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    await state.set_state(States.entering_trade_value)
    await callback.message.answer(texts.TRADE_REGISTER_VALUE)

@router.callback_query(States.entering_trade_id, F.data == "registering-cancel")
async def CancelRegisteringTradeID(callback:CallbackQuery, state:FSMContext):
    await callback.message.delete()
    account_data = await state.get_data()
    await state.set_data({"name":account_data["name"], "password":account_data["password"]})