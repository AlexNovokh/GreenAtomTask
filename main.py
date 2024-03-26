from fastapi import FastAPI, Query
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"You can start_robot or stop_robot"}


# Запуск веб-сервера
if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
