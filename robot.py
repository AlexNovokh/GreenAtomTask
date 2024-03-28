import asyncio
import sys


# Прибавление 1 каждую секунду
async def robot(start_number=0):
    count = start_number
    while True:
        print(count)
        count += 1
        await asyncio.sleep(1)


async def main():
    try:
        start_number = int(sys.argv[1]) if len(sys.argv) == 2 else 0
    except ValueError:  # Если введено не число
        start_number = 0
    task = asyncio.create_task(robot(start_number))
    await task


if __name__ == "__main__":
    asyncio.run(main())
