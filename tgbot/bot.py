import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import save_order

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

PRODUCTS = {
    "hoodie": {
        "name": "🧥 Худи Oversize",
        "price": "$45",
        "photo": "https://sixtynine.com.ua/wp-content/uploads/2024/02/chorne-hudi-regular-no-logo-800x800.jpg"
    },
    "tshirt": {
        "name": "👕 Футболка Basic",
        "price": "$25",
        "photo": "https://sixtynine.com.ua/wp-content/uploads/2022/02/chorna-futbolka-regular-blank.jpg"
    },
    "jeans": {
        "name": "👖 Джинсы Classic",
        "price": "$60",
        "photo": "https://garne.com.ua/img/p/full/119/8034119a.jpg"
    }
}

SIZE_CHART = """📏 *Таблица размеров*

S — рост 160–170 см
M — рост 170–180 см
L — рост 180–190 см
XL — рост 190–200 см

Если сомневаетесь — выбирайте M 👍
"""


class Order(StatesGroup):
    product = State()
    size = State()


def products_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{v['name']} {v['price']}", callback_data=k)]
            for k, v in PRODUCTS.items()
        ]
    )


def size_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="S", callback_data="S"),
                InlineKeyboardButton(text="M", callback_data="M"),
                InlineKeyboardButton(text="L", callback_data="L"),
                InlineKeyboardButton(text="XL", callback_data="XL"),
            ]
        ]
    )


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "✨ *Добро пожаловать в наш магазин одежды!* ✨\n\nВыберите товар ниже 👇",
        reply_markup=products_keyboard(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.in_(PRODUCTS.keys()))
async def choose_product(call: CallbackQuery, state: FSMContext):
    product = PRODUCTS[call.data]

    await state.update_data(product=f"{product['name']} — {product['price']}")

    photo = product["photo"]

    await call.message.answer_photo(
        photo=photo,
        caption=f"*{product['name']}*\nЦена: {product['price']}",
        parse_mode="Markdown"
    )

    await call.message.answer(SIZE_CHART, parse_mode="Markdown")
    await call.message.answer("Выберите размер:", reply_markup=size_keyboard())

    await state.set_state(Order.size)
    await call.answer()


@dp.callback_query(F.data.in_({"S", "M", "L", "XL"}))
async def choose_size(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    product = data["product"]
    size = call.data

    save_order(call.from_user.id, product, size)

    await bot.send_message(
        ADMIN_ID,
        f"🛍 *Новый заказ*\n\n"
        f"{product}\n"
        f"Размер: {size}\n"
        f"User ID: {call.from_user.id}",
        parse_mode="Markdown"
    )

    await call.message.answer(
        "✅ *Заказ принят!*\nНаш менеджер скоро напишет вам 💬",
        parse_mode="Markdown"
    )

    await state.clear()
    await call.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
