from aiogram.fsm.state import StatesGroup, State

class States(StatesGroup):
    loginning_username = State()
    loginning_password = State()

    logged_in = State()

    transfering_name = State()
    transfering_value = State()
    transfering_comment = State()

    entering_trade_id = State()
    entering_trade_value = State()

    buying_tradepack = State()

    entering_pay_id = State()

    trades_managment = State()
    deleting_trade = State()