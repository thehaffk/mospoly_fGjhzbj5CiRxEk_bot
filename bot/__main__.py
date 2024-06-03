import asyncio
import os
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import database_handler as db

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def parse_time(time_str: str) -> int:
    """
    Transfers 1h 2m 3m to minutes integer

    :param time_str:
    :return: integer in minutes
    """
    time_values = {'h': 60, 'm': 1, 'd': 60 * 24}
    time_int = "0"
    for char in time_str:
        char: str
        if char.isdigit():
            time_int += char
            continue

        return int(time_int) * time_values.get(char, 0)

    return 0


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await message.answer('Привет! Я твой TODO-менеджер. Введи /help для списка команд.')


@dp.message_handler(commands=['help'])
async def on_help(message: types.Message):
    await message.answer(
        '/add <описание> <время, используя h, m и d> - добавить задачу\n'
        '/tasks - посмотреть задачи\n/task <id> - посмотреть задачу\n'
        '/edit <id> <новое описание> <новое относительное время> - редактировать задачу\n'
        '/delete <id> - удалить задачу'
    )


@dp.message_handler(commands=['add'])
async def on_add(message: types.Message):
    try:
        user_id = message.from_user.id
        args = message.text.split()[1:]
        description = ' '.join(args[:-1])
        due_date = parse_time(args[-1])
        if due_date <= 0:
            return await message.answer("Неправильный формат времени, используйте `1h` или `7d`")
        due_datetime = datetime.now() + timedelta(minutes=due_date)
        await db.add_task(user_id, description, due_datetime.strftime('%Y-%m-%d %H:%M'))
        await message.answer('Задача добавлена!')
    except Exception as e:
        logging.error(e)
        await message.answer('Ошибка при добавлении задачи. Пример: `/add Написать TODO-бота 7d`')


@dp.message_handler(commands=['tasks'])
async def on_tasks(message: types.Message) -> None:
    user_id = message.from_user.id
    tasks = await db.get_tasks(user_id)
    tasks_text = '\n'.join([f"{task[0]}: {task[2]} - {task[3]}" for task in tasks])
    await message.answer(f"Задачи:\n{tasks_text}")


@dp.message_handler(commands=['task'])
async def on_task(message: types.Message) -> None:
    try:
        user_id = message.from_user.id
        args = message.text.split()[1:]
        task_id = int(args[0])
        task = await db.get_task(user_id, task_id)
        if task:
            await message.answer(f"Задача {task[0]}: {task[2]} - {task[3]}")
        else:
            await message.answer(f"Задача с ID {task_id} не найдена.")
    except Exception as e:
        logging.error(e)
        await message.answer('Ошибка при получении задачи.')


@dp.message_handler(commands=['edit'])
async def on_edit(message: types.Message) -> None:
    try:
        user_id = message.from_user.id
        args = message.text.split()[1:]
        task_id = int(args[0])
        new_description = ' '.join(args[1:-1])
        new_due_date = args[-1]
        due_datetime = datetime.now() + timedelta(minutes=parse_time(new_due_date))
        await db.edit_task(user_id, task_id, new_description, due_datetime.strftime('%Y-%m-%d %H:%M'))
        await message.answer(f"Задача {task_id} отредактирована.")
    except Exception as e:
        logging.error(e)
        await message.answer('Ошибка при редактировании задачи.')


@dp.message_handler(commands=['delete'])
async def on_delete(message: types.Message) -> None:
    try:
        user_id = message.from_user.id
        args = message.text.split()[1:]
        task_id = int(args[0])
        await db.delete_task(user_id, task_id)
        await message.answer(f"Задача {task_id} удалена.")
    except Exception as e:
        logging.error(e)
        await message.answer('Ошибка при удалении задачи.')


async def notify_due_tasks():
    tasks = await db.get_due_tasks()
    for task in tasks:
        try:
            _user_id, description, due_date, _task_id = task
            await bot.send_message(_user_id, f"Задача c описанием "
                                             f" '{description}' "
                                             f" должна быть выполнена до {due_date}!")
            await db.delete_task(user_id=_user_id, task_id=_task_id)
        except Exception as e:
            logging.error(e)
            continue


async def main():
    await db.init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_due_tasks, 'interval', minutes=1)
    scheduler.start()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
