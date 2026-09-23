
# import threading
# import time

# COUNT = 20_000_000

# def square(name):
#     print(f"{name} Started")

#     total = 0
#     for i in range(COUNT):
#         total += i * i

#     print(f"{name} Finished")

# start = time.time()

# t1 = threading.Thread(target=square, args=("Thread-1",))
# t2 = threading.Thread(target=square, args=("Thread-2",))

# t1.start()
# t2.start()

# t1.join()
# t2.join()

# print(f"Total Time: {time.time() - start:.2f}")


import asyncio

# async def task():
#     print("Hello")

# asyncio.run(task())

# import os
# import time
# import requests

# URLS = [
#     "https://picsum.photos/400/300",
#     "https://picsum.photos/401/300",
#     "https://picsum.photos/402/300",
#     "https://picsum.photos/403/300",
#     "https://picsum.photos/404/300",
# ]

# os.makedirs("images", exist_ok=True)


# def download(url, index):
#     print(f"Downloading Image {index}")

#     response = requests.get(url)

#     with open(f"images/image_{index}.jpg", "wb") as f:
#         f.write(response.content)

#     print(f"Downloaded Image {index}")


# start = time.perf_counter()

# for i, url in enumerate(URLS, start=1):
#     download(url, i)

# end = time.perf_counter()

# print("=" * 50)
# print(f"Total Time : {end - start:.2f} sec")
# print("=" * 50)


import asyncio

# async def worker(name):
#     print(f"{name} Started")

#     await asyncio.sleep(3)

#     print(f"{name} Finished")


# async def main():

#     t1 = asyncio.create_task(worker("A"))
#     t2 = asyncio.create_task(worker("B"))
#     t3 = asyncio.create_task(worker("C"))

#     print("Main is doing something...")

#     await asyncio.sleep(5)

#     print("Main completed its work.")

# asyncio.run(main())

import asyncio


# async def download_image(invoice_id):
#     print(f"⬇️ Downloading invoice {invoice_id}...")
#     await asyncio.sleep(2)
#     print(f"✅ Download complete {invoice_id}")
#     return f"image_{invoice_id}.jpg"


# async def extract_text(image):
#     print(f"🔍 OCR processing {image}...")
#     await asyncio.sleep(3)
#     print(f"✅ OCR complete {image}")
#     return f"Text from {image}"


# async def save_to_database(text):
#     print("💾 Saving to database...")
#     await asyncio.sleep(1)
#     print("✅ Saved")

# async def process_invoice(invoice_id):
#     image = await download_image(invoice_id)
#     text = await extract_text(image)
#     await save_to_database(text)

#     return text

# async def main():
#     result = await process_invoice(101)
#     print(result)


# asyncio.run(main())

from fastapi import FastAPI
import asyncio

# Create the FastAPI application
app = FastAPI()


@app.get("/")
async def home():
    return {
        "message": "Mock AI Backend is running!"
    }


@app.get("/download")
async def download(invoice_id: int):

    print(f"📥 Request received for Invoice {invoice_id}")

    # Simulate network delay
    await asyncio.sleep(2)

    print(f"✅ Download completed for Invoice {invoice_id}")

    return {
        "invoice_id": invoice_id,
        "image": f"image_{invoice_id}.jpg"
    }