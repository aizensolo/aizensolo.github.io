from . import checks
import asyncio

async def check_trade_id_is_correct(trade_id:str):
    return await asyncio.to_thread(checks.check_trade_id_is_correct, trade_id)