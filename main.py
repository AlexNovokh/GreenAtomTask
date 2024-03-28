from fastapi import FastAPI, Query
import subprocess
import uvicorn
import psutil
import sqlite3
import datetime

app = FastAPI()

# Название файла, содержащего код робота
filename = "robot.py"
# Название файла, содержащего базу данных
dbname = "robot_history.db"
# Начальное число, время запуска и работы робота
row = [0, 0, 0]


# Проверка состояния робота
def has_started():
    for proc in psutil.process_iter():
        try:
            cmdline = proc.cmdline()
            # Поиск команды запуска файла
            if cmdline and cmdline[0] == "python" and filename in cmdline[1:]:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


@app.get("/")
async def root():
    return {"message": f"You can start_robot, stop_robot or see_history"}


# Запуск робота
@app.get("/start_robot")
async def start_robot(start_number: int = Query(0)):
    if has_started():
        return {"message": f"Robot has already started from number {start_number}"}
    else:
        row[0] = start_number
        row[1] = datetime.datetime.now()
        subprocess.Popen(["python", filename, str(start_number)], stderr=subprocess.PIPE)
        return {"message": f"Robot started from number {start_number}"}


# Остановка робота
@app.get("/stop_robot")
async def stop_robot():
    proc = has_started()
    if proc:
        proc.kill()
        a = datetime.datetime.now() - row[1]
        row[2] = a.seconds
        work_with_db()
        return {"message": f"Robot was stopped"}
    else:
        return {"message": f"Robot wasn't working"}


# Внесение данных в базу данных
def work_with_db():
    with sqlite3.connect(dbname) as db:
        cur = db.cursor()
        cur.execute(open('create.sql').read())  # Создать таблицу
        cur.execute(open('insert.sql').read())  # Вставить значения
        db.commit()


# Просмотр таблицы с историей запусков робота
@app.get("/see_history")
async def see_history():
    with sqlite3.connect(dbname) as db:
        cur = db.cursor()
        try:
            # Показать таблицу
            res = cur.execute(open('show.sql').read())
            db.commit()
            return {"history": f"{res.fetchall()}"}
        except sqlite3.OperationalError:
            return {"message": f"There is no history yet"}


# Запуск веб-сервера
if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
