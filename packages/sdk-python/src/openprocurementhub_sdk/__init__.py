import httpx


class OpenProcurementHubClient:
    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self.base_url=base_url.rstrip('/'); self.headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
    async def tenders(self, limit: int = 50, offset: int = 0) -> dict:
        async with httpx.AsyncClient(headers=self.headers) as client:
            return (await client.get(f"{self.base_url}/api/v1/tenders", params={"limit":limit,"offset":offset})).raise_for_status().json()
