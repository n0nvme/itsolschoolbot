import sqlite3

class TasksDB:

    def _initialize(self):
        self._conn = sqlite3.connect('tasks.db')
        c = self._conn.cursor()
        # create table
        c.execute('''CREATE TABLE tasks
                         (task_id int, task_text text, task_location text, worker_id text, task_status int);''')
        self._conn.commit()
        return c

    def __init__(self):
        try:
            f = open('tasks.db')
            f.close()
            self._conn = sqlite3.connect('tasks.db')
            self._cur = self._conn.cursor()
        except:
            self._cur = self._initialize()

    def _generate_task_id(self):
        self._cur.execute('SELECT MAX(task_id) FROM tasks;')
        self._conn.commit()
        return '1' # REPLACE!!!

    def add_task(self, task_text, task_location):
        self._cur.execute('''INSERT INTO tasks (task_id, task_text, task_location, worker_id, task_status) VALUES 
                            (''' + self._generate_task_id() + ', ' + '''"''' + task_text + '''"''' + ', ' + '''"''' + task_location + '''"''' + ', ' + '0' + ', ' + '0' + ');')
        self._conn.commit()
        print('Written to DB')

    def change_task_status(self, task_id, task_status):
        self._cur.execute('''
                            ''')
        self._conn.commit()


    def _get_task(self, task_id):
        self._cur.execute('SELECT * FROM tasks WHERE id=' + str(task_id))
        self._conn.commit()


    def get_workers_task(self, worker_id):  # Add formatting to string with \n!!!
        self._cur.execute('SELECT * FROM tasks WHERE worker_id="' + str(worker_id) + '"')
        self._conn.commit()

        return '1'

    def get_all_free_tasks(self):  # Add formatting to string with \n!!!
        self._cur.execute('SELECT * FROM tasks WHERE task_status=0')
        self._conn.commit()
        return '1'
