from aiogram import Bot, Dispatcher
import asyncio

from commands import nonlogin, security, general, trades

async def main():
    bot = Bot("BOT_TOKEN_HERE")
    dp = Dispatcher()

    dp.include_routers(nonlogin.router, security.router, general.router, trades.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
