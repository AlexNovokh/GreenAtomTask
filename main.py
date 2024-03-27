from fastapi import FastAPI, Query
import subprocess
import uvicorn
import psutil
import sqlite3
import datetime

app = FastAPI()

# Название файла, содержащего код робота
filename = "robot.py"

arr = [0, 0, 0]


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
        arr[0] = start_number
        arr[1] = datetime.datetime.now()
        subprocess.Popen(["python", filename, str(start_number)], stderr=subprocess.PIPE)
        return {"message": f"Robot started from number {start_number}"}


# Остановка робота
@app.get("/stop_robot")
async def stop_robot():
    proc = has_started()
    if proc:
        proc.kill()
        a = datetime.datetime.now() - arr[1]
        arr[2] = a.seconds
        work_with_db()
        return {"message": f"Robot was stopped"}
    else:
        return {"message": f"Robot wasn't working"}


# Внесение данных в базу данных
def work_with_db():
    with sqlite3.connect("robot_history1.db") as db:
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS rb_history(start_number TEXT, "
                    "start_time TEXT, total_time TEXT)")
        cur.execute(f"INSERT INTO rb_history(start_number, start_time, total_time) VALUES('{arr[0]}', '{arr[1]}', '{arr[2]}')")
        db.commit()


# Просмотр таблицы с историей запусков робота
@app.get("/see_history")
async def see_history():
    with sqlite3.connect("robot_history1.db") as db:
        cur = db.cursor()
        res = cur.execute(f"SELECT * FROM rb_history")
        db.commit()
        return {"history": f"{res.fetchall()}"}


# Запуск веб-сервера
if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
