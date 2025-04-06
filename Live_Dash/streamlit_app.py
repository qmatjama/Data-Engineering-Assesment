
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
from functools import reduce
import streamlit as st
import matplotlib.dates as mdates

st.set_page_config(page_title="Token Tracker Dashboard", layout="wide")
st.title("📡 Token Analytics from XCAP API")

# Caching the data loading step to improve performance
@st.cache_data(ttl=8 * 60 * 60)
def fetch_all_token_transfers():
    base_url = "https://xcap-mainnet.explorer.xcap.network/api/v2/token-transfers"
    MAX_PAGES = 50
    PAGE_DELAY = 0.3
    page = 1
    all_data = []

    while page <= MAX_PAGES:
        try:
            response = requests.get(base_url, params={"page": page}, timeout=10)
            if response.status_code != 200:
                break
            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            all_data.extend(items)
            page += 1
            time.sleep(PAGE_DELAY)
        except requests.exceptions.RequestException:
            break

    return pd.json_normalize(all_data)

# Fetch and preprocess data
df = fetch_all_token_transfers()

fields_to_keep = [
    'transaction_hash', 'token.symbol', 'total.value', 'from.hash',
    'to.hash', 'timestamp', 'token.exchange_rate', 'type', 'token.decimals'
]
df = df[[col for col in fields_to_keep if col in df.columns]].drop_duplicates()

df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.tz_localize(None)
df['total.value'] = pd.to_numeric(df['total.value'], errors='coerce').fillna(0)
df['token.decimals'] = pd.to_numeric(df['token.decimals'], errors='coerce').fillna(18)
df['normalized_value'] = df['total.value'] / (10 ** df['token.decimals'])
df['token.exchange_rate'] = pd.to_numeric(df['token.exchange_rate'], errors='coerce').fillna(0)
df['usd_value'] = df['normalized_value'] * df['token.exchange_rate']

# Task 2 metrics
minted_total = df[df['type'] == 'token_minting']['normalized_value'].sum()
burned_total = df[df['type'] == 'token_burning']['normalized_value'].sum()
total_supply = minted_total - burned_total
unique_tokens = df['token.symbol'].nunique()
total_transactions = len(df)
transferred_tokens = df[df['type'] == 'token_transfer']['normalized_value'].sum()
total_usd_volume = df['usd_value'].sum()

metrics_df = pd.DataFrame({
    "Metric": [
        "Total Asset Supply", "Unique Tokens", "Total Transactions",
        "Tokens Minted", "Tokens Burned", "Tokens Transferred",
        "Total Transaction Volume (USD)"
    ],
    "Value": [
        total_supply, unique_tokens, total_transactions,
        minted_total, burned_total, transferred_tokens,
        total_usd_volume
    ]
})

# Task 3 summary
df_comb = df.copy()
tokens_sent = df_comb[df_comb['type'] == 'token_transfer'].groupby('from.hash')['normalized_value'].sum().reset_index().rename(columns={'from.hash': 'address', 'normalized_value': 'tokens_sent'})
tokens_received = df_comb[df_comb['type'] == 'token_transfer'].groupby('to.hash')['normalized_value'].sum().reset_index().rename(columns={'to.hash': 'address', 'normalized_value': 'tokens_received'})
tokens_minted = df_comb[df_comb['type'] == 'token_minting'].groupby('to.hash')['normalized_value'].sum().reset_index().rename(columns={'to.hash': 'address', 'normalized_value': 'tokens_minted'})
tokens_burned = df_comb[df_comb['type'] == 'token_burning'].groupby('from.hash')['normalized_value'].sum().reset_index().rename(columns={'from.hash': 'address', 'normalized_value': 'tokens_burned'})

dfs = [tokens_minted, tokens_burned, tokens_received, tokens_sent]
from functools import reduce
df_combined = reduce(lambda left, right: pd.merge(left, right, on='address', how='outer'), dfs).fillna(0)

df_combined['token_holding'] = (
    df_combined['tokens_minted'] - df_combined['tokens_burned'] +
    df_combined['tokens_received'] - df_combined['tokens_sent']
)

top10_holdings = df_combined.sort_values(by='token_holding', ascending=False).head(10)
top10_sent = df_combined.sort_values(by='tokens_sent', ascending=False).head(10)[['address', 'tokens_sent']]
top10_received = df_combined.sort_values(by='tokens_received', ascending=False).head(10)[['address', 'tokens_received']]

# === Dashboard Display ===
st.header("📊 Blockchain Summary Metrics")
st.dataframe(metrics_df)

st.subheader("📦 Top 10 Addresses Holding the Most Tokens")
st.dataframe(top10_holdings[['address', 'token_holding']].style.format("{:.6f}"))

st.subheader("📤 Top 10 Addresses by Tokens Sent")
st.dataframe(top10_sent.style.format("{:.6f}"))

st.subheader("📥 Top 10 Addresses by Tokens Received")
st.dataframe(top10_received.style.format("{:.6f}"))

st.markdown("---")
st.markdown("📡 Live Dashboard Powered by XCAP API | Built with ❤️ by Qenehelo")
