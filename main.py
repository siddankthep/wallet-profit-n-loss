import streamlit as st
from src.data import get_pnl, get_wallet_portfolio, get_net_worth
import asyncio
from src.utils import display_net_worth, display_pnl

# --- session state init (do this near the top of your app) ---
if "pnl_sort_by" not in st.session_state:
    st.session_state.pnl_sort_by = "Current Value"
if "pnl_show_pct" not in st.session_state:
    st.session_state.pnl_show_pct = False
if "pnl_data" not in st.session_state:
    st.session_state.pnl_data = None
if "net_worth_data" not in st.session_state:
    st.session_state.net_worth_data = None

NET_WORTH_MAPPINGS = {
    "Hour": "1h",
    "Day": "1d",
    "Backward": "back",
    "Forward": "forward",
    "Descending": "desc",
    "Ascending": "asc",
}


async def main():
    try:
        st.title("Wallet PNL")

        st.write("Enter your wallet address and the date range you want to analyze.")

        wallet_address = st.text_input("Wallet Address")

        with st.sidebar:
            st.title("Net Worth Options")
            sort_type = st.selectbox("Sort Type", ["Descending", "Ascending"], index=0)
            count_type = st.selectbox("Count Type", ["Hour", "Day"], index=1)
            count = st.number_input("Count", value=7, min_value=1, max_value=30)
            direction = st.selectbox("Direction", ["Backward", "Forward"], index=0)

            col1, col2 = st.columns(2)
            with col1:
                date_from = st.date_input("Start Date (optional)", value=None, max_value="today")
            with col2:
                time_from = st.time_input("Start Time (optional)", value=None)

            if date_from and time_from:
                date_str = f"{date_from} {time_from}"
                date_input = date_str
            else:
                date_str = "now"
                date_input = None

            explanation_msg = f"Net Worth data of {count} {count_type.lower()}(s) {direction.lower()} from {date_str} will be retrieved"
            st.caption(explanation_msg)

        submit = st.button("Submit")
        if submit:
            with st.spinner("Retrieving net worth data..."):
                portfolio = await get_wallet_portfolio(wallet_address)
                net_worth = await get_net_worth(
                    wallet_address,
                    NET_WORTH_MAPPINGS[sort_type],
                    count,
                    NET_WORTH_MAPPINGS[direction],
                    date_input,
                    NET_WORTH_MAPPINGS[count_type],
                )
                pnl = await get_pnl(wallet_address, [item.address for item in portfolio.items])

                # Store data in session state so it persists across widget interactions
                st.session_state.net_worth_data = net_worth
                st.session_state.pnl_data = pnl

        # Display data from session state (persists across reruns)
        if st.session_state.net_worth_data is not None:
            st.subheader("Net Worth")
            display_net_worth(st.session_state.net_worth_data)

        if st.session_state.pnl_data is not None:
            st.subheader("PNL")
            display_pnl(st.session_state.pnl_data)

    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
