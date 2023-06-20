import asyncio
import csv
from datetime import datetime

import twooter.db

TEST_FILE = "./chatgpt-twoots.csv"


def read_test_data() -> None:
    data = []

    with open(TEST_FILE, "r") as file:
        csv_reader = csv.reader(file)

        next(csv_reader)  # Skip header

        for row in csv_reader:
            data.append({
                "text": row[0],
                "tag": row[1],
                "timestamp": datetime.fromisoformat(row[2]),
            })

    return data


async def main():
    await twooter.db.init()

    try:
        messages = [twooter.db.Message(**msg) for msg in read_test_data()]

        result = await twooter.db.Message.bulk_create(messages)

        print(f"Success, inserted {len(result)} messages")
    finally:
        await twooter.db.teardown()


if __name__ == "__main__":
    asyncio.run(main())
