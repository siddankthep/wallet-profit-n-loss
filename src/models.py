from pydantic import BaseModel
from typing import List, Optional, Dict


# Net Worth
class NetWorthHistoryItem(BaseModel):
    timestamp: Optional[str] = None
    net_worth: Optional[float] = None
    net_worth_change: Optional[float] = None
    net_worth_change_percent: Optional[float] = None


class NetWorthResponse(BaseModel):
    wallet_address: Optional[str] = None
    currency: Optional[str] = None
    current_timestamp: Optional[str] = None
    past_timestamp: Optional[str] = None
    history: List[NetWorthHistoryItem] = []


# Portfolio
class WalletPortfolioItem(BaseModel):
    address: Optional[str] = None
    decimals: Optional[int] = None
    balance: Optional[int] = None
    uiAmount: Optional[float] = None
    chainId: Optional[str] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    icon: Optional[str] = None
    logoURI: Optional[str] = None
    priceUsd: Optional[float] = None
    valueUsd: Optional[float] = None
    isScaledUiToken: Optional[bool] = None
    multiplier: Optional[float] = None


class WalletPortfolio(BaseModel):
    items: List[WalletPortfolioItem] = []


# PNL
class PnlMeta(BaseModel):
    address: Optional[str] = None
    currency: Optional[str] = None
    holding_check: Optional[bool] = None
    time: Optional[str] = None


class TokenCounts(BaseModel):
    total_buy: Optional[int] = None
    total_sell: Optional[int] = None
    total_trade: Optional[int] = None


class TokenQuantity(BaseModel):
    total_bought_amount: Optional[float] = None
    total_sold_amount: Optional[float] = None
    holding: Optional[float] = None


class TokenCashflowUsd(BaseModel):
    cost_of_quantity_sold: Optional[float] = None
    total_invested: Optional[float] = None
    total_sold: Optional[float] = None
    current_value: Optional[float] = None


class TokenPnl(BaseModel):
    realized_profit_usd: Optional[float] = None
    realized_profit_percent: Optional[float] = None
    unrealized_usd: Optional[float] = None
    unrealized_percent: Optional[float] = None
    total_usd: Optional[float] = None
    total_percent: Optional[float] = None
    avg_profit_per_trade_usd: Optional[float] = None


class TokenPricing(BaseModel):
    current_price: Optional[float] = None
    avg_buy_cost: Optional[float] = None
    avg_sell_cost: Optional[float] = None


class TokenData(BaseModel):
    symbol: Optional[str] = None
    decimals: Optional[int] = None
    counts: TokenCounts = None
    quantity: TokenQuantity = None
    cashflow_usd: TokenCashflowUsd = None
    pnl: TokenPnl = None
    pricing: TokenPricing = None


class WalletPnlResponse(BaseModel):
    meta: PnlMeta = None
    tokens: Dict[str, TokenData]
