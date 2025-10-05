import pandas as pd
import streamlit as st
from src.models import WalletPnlResponse, NetWorthResponse
from datetime import datetime
import altair as alt


def display_net_worth(net_worth: NetWorthResponse):
    """Display net worth data as a line chart"""
    if not net_worth or not net_worth.history:
        st.warning("No net worth data available")
        return

    # Prepare data for charting
    timestamps = []
    values = []

    for item in net_worth.history:
        if item.timestamp and item.net_worth is not None:
            # Convert timestamp to datetime for better display
            try:
                dt = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))
                timestamps.append(dt)
            except (ValueError, AttributeError):
                timestamps.append(item.timestamp)
            values.append(item.net_worth)

    if not timestamps or not values:
        st.warning("No valid net worth data points available")
        return

    # Create DataFrame for charting
    df = pd.DataFrame({"Timestamp": timestamps, "Net Worth (USD)": values})

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")

    y_min = df["Net Worth (USD)"].min()
    y_max = df["Net Worth (USD)"].max()
    pad = max(0.05, (y_max - y_min) * 0.3)  # 30% padding or at least 5c

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Timestamp:T",
                title="Timestamp",
                axis=alt.Axis(
                    format="%b %d",
                    labelAngle=-45,  # rotate
                    labelAlign="right",  # align text with the tick
                    labelBaseline="top",  # baseline for angled labels
                ),
            ),
            y=alt.Y(
                "Net Worth (USD):Q",
                title="Net Worth (USD)",
                scale=alt.Scale(zero=False, domain=[y_min - pad, y_max + pad]),
            ),
            tooltip=[
                alt.Tooltip("Timestamp:T", title="Time"),
                alt.Tooltip("Net Worth (USD):Q", format="$.2f", title="Net Worth"),
            ],
        )
        .properties(height=300)
    )
    # chart = chart.interactive()

    st.altair_chart(chart, use_container_width=True)

    # Display summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Net Worth", f"${values[-1]:,.2f}")
    with col2:
        if len(values) > 1:
            change = values[-1] - values[0]
            st.metric("Change", f"${change:,.2f}", delta=f"{change:,.2f}")
    with col3:
        if len(values) > 1:
            change_percent = ((values[-1] - values[0]) / values[0]) * 100
            st.metric("Change %", f"{change_percent:.2f}%", delta=f"{change_percent:.2f}%")


def display_pnl(pnl: WalletPnlResponse):
    if not pnl or not pnl.tokens:
        st.warning("No PNL data available")
        return

    # Build a tidy DataFrame (same content as your table)
    rows = []
    for token_addr, token_data in pnl.tokens.items():
        rows.append(
            {
                "Token Address": token_addr,
                "Symbol": token_data.symbol or token_addr[:6],
                "Total Trades": (token_data.counts.total_trade if token_data.counts else 0) or 0,
                "Buys": (token_data.counts.total_buy if token_data.counts else 0) or 0,
                "Sells": (token_data.counts.total_sell if token_data.counts else 0) or 0,
                "Holding": (token_data.quantity.holding if token_data.quantity else 0) or 0,
                "Total Invested": (token_data.cashflow_usd.total_invested if token_data.cashflow_usd else 0) or 0.0,
                "Total Sold": (token_data.cashflow_usd.total_sold if token_data.cashflow_usd else 0) or 0.0,
                "Current Value": (token_data.cashflow_usd.current_value if token_data.cashflow_usd else 0) or 0.0,
                "Realized Profit": (token_data.pnl.realized_profit_usd if token_data.pnl else 0) or 0.0,
                "Unrealized Profit": (token_data.pnl.unrealized_usd if token_data.pnl else 0) or 0.0,
                "Total PNL": (token_data.pnl.total_usd if token_data.pnl else 0) or 0.0,
                "Total PNL %": (token_data.pnl.total_percent if token_data.pnl else 0) or 0.0,
                "Avg Buy Price": (token_data.pricing.avg_buy_cost if token_data.pricing else 0) or 0.0,
                "Avg Sell Price": (token_data.pricing.avg_sell_cost if token_data.pricing else 0) or 0.0,
                "Current Price": (token_data.pricing.current_price if token_data.pricing else 0) or 0.0,
            }
        )
    df = pd.DataFrame(rows)

    # Controls

    # Portfolio summary (top KPIs)
    k1, k2 = st.columns(2)
    total_invested = df["Total Invested"].sum()
    current_value = df["Current Value"].sum()
    realized = df["Realized Profit"].sum()
    unrealized = df["Unrealized Profit"].sum()
    total_pnl = df["Total PNL"].sum()
    total_pct = (total_pnl / total_invested * 100) if total_invested else 0.0

    k1.metric("Current Value", f"${current_value:,.2f}")
    k2.metric("Invested", f"${total_invested:,.2f}")

    k3, k4 = st.columns(2)
    k3.metric("P&L (Total)", f"${total_pnl:,.2f}", delta=f"{total_pct:.2f}%")
    k4.metric("Realized / Unrealized", f"${realized:,.2f} / ${unrealized:,.2f}")

    # Card grid (3 per row)
    N = len(df)
    for i in range(0, N):
        row = df.iloc[i]

        pnl_val = row["Total PNL"]
        pnl_pct = row["Total PNL %"]

        with st.container(border=True):
            st.subheader(row["Symbol"])
            st.caption(row["Token Address"])
            k1, k2 = st.columns(2)
            k1.metric("Current Value", f"${row['Current Value']:,.2f}")
            k2.metric("Holding", f"{row['Holding']:.4f}")

            # Mini comparison chart (invested vs current)
            mini = pd.DataFrame(
                {
                    "Label": ["Invested", "Current"],
                    "USD": [row["Total Invested"], row["Current Value"]],
                }
            )
            chart = (
                alt.Chart(mini)
                .mark_bar()
                .encode(
                    x=alt.X("Label:N", title=None, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("USD:Q", title="USD"),
                    tooltip=[alt.Tooltip("Label:N"), alt.Tooltip("USD:Q", format="$.2f")],
                )
                .properties(height=120)
            )
            st.altair_chart(chart, use_container_width=True)

            # P&L strip
            pcol1, pcol2, pcol3 = st.columns(3)
            pcol1.metric("Realized", f"${row['Realized Profit']:,.2f}")
            pcol2.metric("Unrealized", f"${row['Unrealized Profit']:,.2f}")
            pcol3.metric("Total P&L", f"${pnl_val:,.2f}", delta=f"{pnl_pct:.2f}%")

            with st.expander("Details"):
                d1, d2, d3 = st.columns(3)
                d1.metric("Trades", int(row["Total Trades"]))
                d2.metric("Buys", int(row["Buys"]))
                d3.metric("Sells", int(row["Sells"]))

                d4, d5, d6 = st.columns(3)
                d4.metric("Avg Buy", f"${row['Avg Buy Price']:.6f}")
                d5.metric("Avg Sell", f"${row['Avg Sell Price']:.6f}")
                d6.metric("Price", f"${row['Current Price']:.6f}")

                st.caption("Cashflow")
                cash = pd.DataFrame(
                    {
                        "Type": ["Invested", "Sold", "Current Value"],
                        "USD": [row["Total Invested"], row["Total Sold"], row["Current Value"]],
                    }
                )
                cash_chart = (
                    alt.Chart(cash)
                    .mark_bar()
                    .encode(
                        x=alt.X("Type:N", title=None),
                        y=alt.Y("USD:Q", title="USD"),
                        tooltip=[alt.Tooltip("Type:N"), alt.Tooltip("USD:Q", format="$.2f")],
                    )
                    .properties(height=140)
                )
                st.altair_chart(cash_chart, use_container_width=True)
