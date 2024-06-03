import datetime

import aiosqlite


async def init_db():
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                due_date TEXT NOT NULL
            )
        ''')
        await db.commit()


async def add_task(user_id, description, due_date):
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('INSERT INTO tasks (user_id, description, due_date) VALUES (?, ?, ?)',
                         (user_id, description, due_date))
        await db.commit()


async def get_tasks(user_id):
    async with aiosqlite.connect('tasks.db') as db:
        cursor = await db.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
        tasks = await cursor.fetchall()
        return tasks


async def get_task(user_id, task_id):
    async with aiosqlite.connect('tasks.db') as db:
        cursor = await db.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        task = await cursor.fetchone()
        return task


async def edit_task(user_id, task_id, new_description, new_due_date):
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('UPDATE tasks SET description = ?, due_date = ? WHERE id = ? AND user_id = ?',
                         (new_description, new_due_date, task_id, user_id))
        await db.commit()


async def delete_task(user_id, task_id):
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        await db.commit()


async def get_due_tasks():
    async with aiosqlite.connect('tasks.db') as db:
        cursor = await db.execute('SELECT user_id, description, due_date, id FROM tasks WHERE due_date = ?',
                                  (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),))
        tasks = await cursor.fetchall()
        return tasks
