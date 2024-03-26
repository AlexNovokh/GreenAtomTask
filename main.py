from fastapi import FastAPI, Query
import subprocess
import uvicorn
import psutil

app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"You can start_robot, stop_robot or see_history"}


# Запуск робота
@app.get("/start_robot")
async def start_robot(start_number: int = Query(0)):
    subprocess.Popen(["python", "robot.py", str(start_number)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"message": f"Robot started from number {start_number}"}


# Остановка робота
@app.get("/stop_robot")
async def stop_robot():
    for proc in psutil.process_iter():
        try:
            cmdline = proc.cmdline()
            if cmdline and cmdline[0] == "python" and "robot.py" in cmdline[1:]:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return {"message": f"Robot was stopped"}


# Запуск веб-сервера
if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
