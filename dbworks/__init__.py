from . import login, transactions, varied
import asyncio

async def check_if_username_exists(name:str, db_name:str):
    return await asyncio.to_thread(login.check_is_username_exists, name, db_name)

async def check_if_valid_password(name:str, password:str, db_name:str):
    return await asyncio.to_thread(login.check_is_valid_password, name, password, db_name)

async def check_balance(name:str, password:str, db_name:str):
    return await asyncio.to_thread(transactions.check_balance, name, password, db_name)

async def transfer(name:str, password:str, value:float, endpoint:str, db_name:str):
    return await asyncio.to_thread(transactions.transfer, name, password, value, endpoint, db_name)

async def is_trade_id_avaliable(trade_id:str, db_name:str):
    return await asyncio.to_thread(varied.is_trade_id_avaliable, trade_id, db_name)

async def create_trade_id(trade_id:str, creator_name:str, password:str, value:float, db_name:str):
    return await asyncio.to_thread(varied.create_trade_id, trade_id, creator_name, password, value, db_name)

async def how_much_trade_ids_on_user(name:str, db_name:str):
    return await asyncio.to_thread(varied.how_much_trade_ids_on_user, name, db_name)

async def buy_tradepack(name:str, password:str, value:float, db_name:str):
    return await asyncio.to_thread(varied.buy_tradepack, name, password, value, db_name)

async def is_tradepack_bought(name:str, db_name:str):
    return await asyncio.to_thread(varied.is_tradepack_bought, name, db_name)

async def search_trade_id(id:str, db_name:str):
    return await asyncio.to_thread(varied.search_trade_id, id, db_name)

async def get_trade_ids_by_user(name:str, db_name:str):
    return await asyncio.to_thread(varied.get_trade_ids_by_user, name, db_name)

async def delete_trade_id(name:str, password:str, id:str, db_name:str):
    return await asyncio.to_thread(varied.delete_trade_id, name, password, id, db_name)

async def get_top_by_money(db_name:str):
    return await asyncio.to_thread(varied.get_top_by_money, db_name)