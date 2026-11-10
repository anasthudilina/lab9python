import asyncio
import httpx

async def fetch_account_balance(client: httpx.AsyncClient, base_url: str, account_number: str, semaphore: asyncio.Semaphore) -> dict:
    """Асинхронний запит з обмеженням Semaphore, retry та timeout."""
    async with semaphore:
        for attempt in range(3):
            try:
                # timeout=2.0 для кожного запиту
                response = await asyncio.wait_for(
                    client.get(f"{base_url}/accounts/search?number={account_number}"),
                    timeout=2.0
                )
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, asyncio.TimeoutError, httpx.HTTPStatusError) as e:
                if attempt == 2: # Якщо це остання спроба
                    return {"account_number": account_number, "error": str(e)}
                await asyncio.sleep(1) # Затримка перед retry

async def fetch_batch_balances(account_numbers: list[str], base_url: str) -> list[dict]:
    """Паралельне завантаження з використанням Task, gather та Semaphore."""
    semaphore = asyncio.Semaphore(5) # Максимум 5 одночасних запитів
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = [
            asyncio.create_task(
                fetch_account_balance(client, base_url, num, semaphore)
            )
            for num in account_numbers
        ]
        # gather збирає результати всіх паралельних тасків
        results = await asyncio.gather(*tasks)
        return list(results)