
import asyncio
import time
import httpx


async def fetch_invoice(invoice_id):

    print(f"➡️ Sending request for Invoice {invoice_id}")

    async with httpx.AsyncClient() as client:

        response = await client.get(
            "http://127.0.0.1:8005/download",
            params={"invoice_id": invoice_id}
        )

    data = response.json()

    print(
        f"⬅️ Received | Invoice={data['invoice_id']} | Image={data['image']}"
    )

    return data


async def main():

    start = time.perf_counter()

    results = await asyncio.gather(
        fetch_invoice(101),
        fetch_invoice(102),
        fetch_invoice(103),
        fetch_invoice(104),
        fetch_invoice(105),
    )

    end = time.perf_counter()

    print("\nResults")
    print(results)

    print(f"\nTotal Time = {end-start:.2f} seconds")


asyncio.run(main())