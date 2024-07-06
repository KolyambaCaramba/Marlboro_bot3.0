import logging
import sqlite3
from aiogram import types
from aiogram.dispatcher.filters.command import Command
from aiogram.utils.callback_data import CallbackData

lastm_callback_data = CallbackData("lastm", "play_date")
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="🏆 Последние матчи 🏆", callback_data="lastm"),
        types.KeyboardButton(text="🏃‍♂️ Список игроков 🏃‍♂️", callback_data="players")],
        [types.KeyboardButton(text="💵 Результаты команды 💵", callback_data="results")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню"
    )
    await message.answer("⚽ Добрый день, вы попали в Marlboro Bot! ⚽\n⚽ Выберите пункт меню ⚽", reply_markup=keyboard)


@dp.message(Command("lastm"))
async def cmd_results(message: types.Message):
    conn = sqlite3.connect('mbr1.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT scored, missed, opponent, play_date FROM matches")
        results_list = cursor.fetchall()

        if not results_list:
            await message.answer("Нет результатов матчей.")
            return

        # Формируем текстовый список результатов
        results_list_text = "Последние матчи команды:\n" + "\n".join(
            f"Marlboro  ( {scored}:{missed} )  {opponent}  -  {play_date}" for scored, missed, opponent, play_date in
            results_list
        )

        # Создаем список кнопок с оппонентами
        buttons = []
        for scored, missed, opponent, play_date in results_list:
            buttons.append(types.InlineKeyboardButton(text=f"({scored}:{missed}) - {opponent}",
                                                      callback_data=f"lastm_{play_date}"))

        # Разбиваем список кнопок на две колонки
        columns = 2
        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[buttons[i:i + columns] for i in range(0, len(buttons), columns)])

        # Отправляем сообщение с результатами и inline клавиатурой
        await message.answer("Выберите матч:\n\n" + results_list_text, reply_markup=inline_keyboard)
    finally:
        conn.close()

@dp.message(Command("players"))
async def players_handler(message: types.Message):
    conn = sqlite3.connect('mbr1.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT last_name FROM players")
        player_list = cursor.fetchall()

        if not player_list:
            await message.answer("Нет игроков.")
            return

        buttons = []
        for last_name in player_list:
            buttons.append(types.InlineKeyboardButton(text=last_name, callback_data=f"player_{last_name}"))

        columns = 2
        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[buttons[i:i + columns] for i in range(0, len(buttons), columns)])

        await message.answer("Выберите игрока:", reply_markup=inline_keyboard)
    finally:
        cursor.close()
        conn.close()

@dp.callback_query_handler(lambda call: call.data.startswith('player_'))
async def player_callback_handler(call: types.CallbackQuery):
    last_name = call.data.split('_')[1]
    await call.message.answer(f"Вы выбрали игрока {last_name}.")

@dp.message(Command("results"))
async def results_handler(msg: types.Message):
    conn = sqlite3.connect('mbr1.db')
    cursor = conn.cursor()

    try:
        # Извлекаем данные о сыгранных матчах из таблицы matches
        cursor.execute("SELECT count(*) FROM matches")
        matches_played = cursor.fetchone()[0]

        # Извлекаем данные о забитых голах из таблицы goal_details
        cursor.execute("SELECT count(*) FROM goal_details WHERE who_score != 0")
        goal_scored = cursor.fetchone()[0]

        # Извлекаем данные о количестве ассистов из таблицы goal_details
        cursor.execute("SELECT count(*) FROM goal_details WHERE who_assist != 0")
        goal_assists = cursor.fetchone()[0]

        # Так можно посчитать число выигранных матчей
        cursor.execute("SELECT count(match_id) from matches where scored > missed;")
        match_won = cursor.fetchone()[0]

        # Так можно посчитать число выигранных матчей
        cursor.execute("SELECT avg(scored) from matches")
        scored_avg = cursor.fetchone()[0]
        scored_avg = round(scored_avg, 2)

        # Так можно посчитать число выигранных матчей
        cursor.execute("SELECT avg(missed) from matches")
        missed_avg = cursor.fetchone()[0]
        missed_avg = round(missed_avg, 2)

        cursor.execute(
            'SELECT  who_assist, count(*) FROM goal_details GROUP BY who_assist ORDER BY count(*) DESC limit 3')
        res1 = cursor.fetchall()

        # Формируем сообщение с данными команды
        message = f"Результаты ФК 🚬Marlboro🚬:\n\n"
        message += f"Число сыгранных матчей - {matches_played}\n"
        message += f"Забито голов - {goal_scored}\n"
        message += f"Число ассистов - {goal_assists}\n"
        message += f"Матчей выиграно - {match_won}\n"
        message += f"Забито в среднем за игру - {scored_avg}\n"
        message += f"Пропущено в среднем за игру - {missed_avg}\n"

        # Отправляем сообщение с результатами команды
        await msg.answer(message)

    finally:
        cursor.close()
        conn.close()