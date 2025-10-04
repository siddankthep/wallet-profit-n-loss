from typing import Optional
import httpx
from src.models import WalletPnlResponse, WalletPortfolio, NetWorthResponse
import pprint
import streamlit as st


BASE_URL = "https://public-api.birdeye.so"
HEADERS = {
    "accept": "application/json",
    "x-api-key": st.secrets["BIRDEYE_API_KEY"],
    "chain": "solana",
}


async def get_pnl(wallet_address: str, token_addresses: list[str]):
    url = f"{BASE_URL}/wallet/v2/pnl"
    params = {
        "wallet": wallet_address,
        "token_addresses": ",".join(token_addresses),
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=HEADERS)
        data = response.json()

        print("PNL DATA")
        pprint.pprint(data)
        if response.status_code == 200:
            return WalletPnlResponse(**data.get("data"))
        else:
            raise Exception(data.get("message"))


async def get_wallet_portfolio(wallet_address: str):
    url = f"{BASE_URL}/v1/wallet/token_list"
    params = {
        "wallet": wallet_address,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=HEADERS)
        data = response.json()

        print("PORTFOLIO DATA")
        pprint.pprint(data)
        if data.get("success"):
            return WalletPortfolio(**data.get("data"))
        else:
            raise Exception(data.get("message"))


async def get_net_worth(
    wallet_address: str,
    sort_type: str,
    count: Optional[int] = None,
    direction: Optional[str] = None,
    time: Optional[str] = None,
    count_type: Optional[str] = None,
):
    """
    Get the net worth chart for a wallet
    Args:
        wallet_address (str): wallet address
        sort_type (str): "desc" or "asc", defaults to "desc"
        count (int): 1 to 30, defaults to 7
        direction (str): "back" or "forward", defaults to "back"
        time (str): time to get net worth from, defaults to current time
        count_type (str): "1h" or "1d", defaults to "1d"
    """
    url = f"{BASE_URL}/wallet/v2/net-worth"
    params = {
        "wallet": wallet_address,
        "count": count,
        "direction": direction,
        "time": time,
        "type": count_type,
        "sort_type": sort_type,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=HEADERS)
        data = response.json()

        print("NET WORTH DATA")
        pprint.pprint(data)
        if data.get("success"):
            return NetWorthResponse(**data.get("data"))
        else:
            raise Exception(data.get("message"))
