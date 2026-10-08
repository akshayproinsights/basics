# import asyncio
# import time

# # async def test_as():
# #     print("Test inside start ...")
# #     await asyncio.sleep(5)
# #     print("Test inside Enddd ...")

# # asyncio.run(test_as())

# # import time

# async def download_customer():
#     print("Customer request started")
#     await asyncio.sleep(3)
#     print("Customer received")

# async def download_invoice():
#     print("Invoice request started")
#     await asyncio.sleep(2)
#     print("Invoice received")


# # asyncio.run(download_customer())  # this start and finish run at a same time --> wrong
# ## “Create an event loop, run this async program until it is completely finished, then close the event loop.”
# # asyncio.run(download_invoice())


# # 3  
# # async def main():      # this works pefectly by creating task ***
# #     task1 = asyncio.create_task(download_customer())
# #     task2 = asyncio.create_task(download_invoice())

# #     await task1
# #     await task2

# # asyncio.run(main())  # 

# # async def main():                 # this is still taking 5 mins beacuse its not doing in background 
# #     await download_customer()
# #     await download_invoice()


# # asyncio.run(main())

# async def main():                    #_________##___ we must do main() function  to use .gather
#     await asyncio.gather(download_customer(),download_invoice())

# asyncio.run(main()) 


import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
# ==========================================================
# 1. ASYNC
# Imagine this is an external HTTP API call
# ==========================================================

async def download_document(document_id: int):
    print(f"[ASYNC] Downloading document {document_id}...")

    # Imagine we're waiting for AWS S3 / HTTP API
    await asyncio.sleep(10)

    print(f"[ASYNC] Document {document_id} downloaded")

    return f"document_{document_id}.pdf"


# ==========================================================
# 2. THREAD
# Imagine this is an OLD blocking PDF library
# It does NOT support async/await
# ==========================================================

def read_pdf_with_old_library(filename: str):
    print(f"[THREAD] Reading {filename}...")

    # Imagine old PDF library is blocking here
    time.sleep(3)

    print(f"[THREAD] Finished reading {filename}")

    return "Invoice text: customer bought 100 products"


# ==========================================================
# 3. MULTIPROCESSING
# CPU-heavy Python calculation
# ==========================================================

def heavy_document_analysis(text: str):
    print("[PROCESS] Heavy analysis started")

    total = 0

    # Simulate CPU-heavy work
    for i in range(20_000_000):
        total += i * i

    print("[PROCESS] Heavy analysis finished")

    return {
        "text_length": len(text),
        "calculation": total
    }


# ==========================================================
# MAIN ASYNC APPLICATION
# ==========================================================

async def process_document(document_id: int):

    print("\n--- Document processing started ---\n")

    # ------------------------------------------------------
    # STEP 1: NETWORK WAITING
    # Use ASYNC
    # ------------------------------------------------------

    filename = await download_document(document_id)


    # ------------------------------------------------------
    # STEP 2: BLOCKING OLD LIBRARY
    # Put it into another THREAD
    # ------------------------------------------------------

    text = await asyncio.to_thread(
        read_pdf_with_old_library,
        filename
    )


    # ------------------------------------------------------
    # STEP 3: CPU-HEAVY WORK
    # Put it into another PROCESS
    # ------------------------------------------------------

    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as pool:

        result = await loop.run_in_executor(
            pool,
            heavy_document_analysis,
            text
        )


    print("\n--- Final Result ---")
    print(result)


# ==========================================================
# PROGRAM ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    asyncio.run(process_document(101))



## Make 20 API calls, but allow only 5 calls at the same time, and give each individual API call a timeout.

