from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

api = "#######"
bot = Bot(token=api)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
button_3 = KeyboardButton(text='Купить')
kb.row(button_1, button_2, button_3)

catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
        InlineKeyboardButton(text='Продукт 1', callback_data='product_buying'),
        InlineKeyboardButton(text='Продукт 2', callback_data='product_buying'),
        InlineKeyboardButton(text='Продукт 3', callback_data='product_buying'),
        InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
         ]
    ]
)

combined_kb = InlineKeyboardMarkup(row_width=2)
combined_kb.add(InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
    InlineKeyboardButton(text='Формулы расчета', callback_data='formulas'))

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет, я бот помогающий твоему здоровью!', reply_markup = kb)

@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    for i in range(1, 5):
            await message.answer(text = f'Название: Продукт_{i}, Описание: Описание_{i}, Цена: {i*100}')
            with open(f'files2/{i}.png', 'rb') as img:
                await message.answer_photo(img)
    await message.answer(text="Выберите продукт для покупки", reply_markup=catalog_kb)

@dp.callback_query_handler(text =['product_buying'])
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=combined_kb)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("Упрощенный вариант формулы Миффлина-Сан Жеора: "
                              "для мужчин: 10 * вес (кг) + 6,25 * рост (см) – 5 * возраст (г) + 5; "
                              "для женщин: 10 * вес (кг) + 6,25 * рост (см) – 5 * возраст (г) - 161")
    await call.answer()

@dp.callback_query_handler(text =['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст, лет:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост, сантиметры:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес, килограммы:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    norm_calory = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    await message.answer(f'Ваша норма калорий: {norm_calory} в сутки')
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
