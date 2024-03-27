from fastapi import FastAPI, Query
import subprocess
import uvicorn
import psutil
import sqlite3
import datetime

app = FastAPI()

# Название файла, содержащего код робота
filename = "robot.py"

arr = ['0', '', '']


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
    return {"message": f"You can start_robot, stop_robot"}

# Запуск робота
@app.get("/start_robot")
async def start_robot(start_number: int = Query(0)):
    if has_started():
        return {"message": f"Robot has already started from number {start_number}"}
    else:
        arr[0] = f"{start_number}"
        arr[1] = f"{datetime.datetime.now()}"
        subprocess.Popen(["python", filename, str(start_number)], stderr=subprocess.PIPE)
        return {"message": f"Robot started from number {start_number}"}


# Остановка робота
@app.get("/stop_robot")
async def stop_robot():
    proc = has_started()
    if proc:
        proc.kill()
        arr[2] = f"{datetime.datetime.now()}"
        work_with_db()
        return {"message": f"Robot was stopped"}
    else:
        return {"message": f"Robot wasn't working"}


# Внесение данных в базу данных
def work_with_db():
    con = sqlite3.connect("new1.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS rb_history(start_number TEXT, "
                "start_time TEXT, total_time TEXT)")
    cur.execute(f"INSERT INTO rb_history(start_number, start_time, total_time) VALUES('{arr[0]}', '{arr[1]}', '{arr[2]}')")
    con.commit()
    con.close()


# Просмотр таблицы с историей запусков робота
@app.get("/see_history")
def see_history():
    return {"message": f"History table will be here"}


# Запуск веб-сервера
if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
