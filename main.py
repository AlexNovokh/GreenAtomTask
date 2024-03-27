from fastapi import FastAPI, Query
import subprocess
import uvicorn
import psutil

app = FastAPI()

# Название файла, содержащего код робота
filename = "robot.py"

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
        subprocess.Popen(["python", filename, str(start_number)], stderr=subprocess.PIPE)
        return {"message": f"Robot started from number {start_number}"}


# Остановка робота
@app.get("/stop_robot")
async def stop_robot():
    proc = has_started()
    if proc:
        proc.kill()
        return {"message": f"Robot was stopped"}
    else:
        return {"message": f"Robot wasn't working"}


# Запуск веб-сервера
if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
