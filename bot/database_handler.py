import aiosqlite

async def init_db():
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                due_date TEXT NOT NULL
            )
        ''')
        await db.commit()

async def add_task(description, due_date):
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('INSERT INTO tasks (description, due_date) VALUES (?, ?)', (description, due_date))
        await db.commit()

async def get_tasks():
    async with aiosqlite.connect('tasks.db') as db:
        cursor = await db.execute('SELECT * FROM tasks')
        tasks = await cursor.fetchall()
        return tasks

async def get_task(task_id):
    async with aiosqlite.connect('tasks.db') as db:
        cursor = await db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = await cursor.fetchone()
        return task

async def edit_task(task_id, new_description, new_due_date):
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('UPDATE tasks SET description = ?, due_date = ? WHERE id = ?',
                         (new_description, new_due_date, task_id))
        await db.commit()

async def delete_task(task_id):
    async with aiosqlite.connect('tasks.db') as db:
        await db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        await db.commit()
