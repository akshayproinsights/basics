import asyncio
import time

# async def test_as():
#     print("Test inside start ...")
#     await asyncio.sleep(5)
#     print("Test inside Enddd ...")

# asyncio.run(test_as())

# import time

async def download_customer():
    print("Customer request started")
    await asyncio.sleep(3)
    print("Customer received")

async def download_invoice():
    print("Invoice request started")
    await asyncio.sleep(2)
    print("Invoice received")


# asyncio.run(download_customer())  # this start and finish run at a same time --> wrong
## “Create an event loop, run this async program until it is completely finished, then close the event loop.”
# asyncio.run(download_invoice())


# 3  
# async def main():      # this works pefectly by creating task ***
#     task1 = asyncio.create_task(download_customer())
#     task2 = asyncio.create_task(download_invoice())

#     await task1
#     await task2

# asyncio.run(main())  # 

# async def main():                 # this is still taking 5 mins beacuse its not doing in background 
#     await download_customer()
#     await download_invoice()


# asyncio.run(main())

async def main():                    #_________##___ we must do main() function  to use .gather
    await asyncio.gather(download_customer(),download_invoice())

asyncio.run(main()) 
