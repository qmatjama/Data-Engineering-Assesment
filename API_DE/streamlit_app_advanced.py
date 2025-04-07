
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

st.set_page_config(page_title="Advanced Token Insights", layout="wide")
st.title("📊 Advanced Token Analytics Dashboard")

@st.cache_data
def load_data():
    excel_path = "../DE_Assesment_Results.xlsx"
    df = pd.read_excel(excel_path, sheet_name="Total_cleaned_records", parse_dates=["timestamp"])
    return df

df = load_data()
df['hour'] = df['timestamp'].dt.hour
df['date'] = df['timestamp'].dt.date

# Sidebar filters
all_tokens = df['token.symbol'].dropna().unique().tolist()
all_types = df['type'].dropna().unique().tolist()
min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()

st.sidebar.header("🔍 Filter Data")
selected_token = st.sidebar.selectbox("Select Token", ["All"] + all_tokens)
selected_type = st.sidebar.selectbox("Select Type", ["All"] + all_types)
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

df_filtered = df.copy()
if selected_token != "All":
    df_filtered = df_filtered[df_filtered['token.symbol'] == selected_token]
if selected_type != "All":
    df_filtered = df_filtered[df_filtered['type'] == selected_type]
df_filtered = df_filtered[
    (df_filtered['timestamp'].dt.date >= date_range[0]) &
    (df_filtered['timestamp'].dt.date <= date_range[1])
]

# USD Value Distribution
st.subheader("💰 USD Value Distribution")
fig1, ax1 = plt.subplots(figsize=(6, 3))
ax1.hist(df_filtered['usd_value'], bins=50, color='skyblue')
ax1.set_xlabel("USD Value")
ax1.set_ylabel("Frequency")
st.pyplot(fig1)
st.dataframe(df_filtered[['timestamp', 'token.symbol', 'usd_value']].sort_values(by='usd_value', ascending=False).head(10))

# Token Utilization Pattern
st.subheader("🧠 Token Utilization Pattern (Pivot Table)")
pivot_util = pd.pivot_table(df_filtered, values="normalized_value", index="token.symbol", columns="type", aggfunc="sum", fill_value=0)
st.dataframe(pivot_util)

# Top Tokens by USD Value
st.subheader("🏁 Top Tokens by USD Value")
top_usd = df_filtered.groupby("token.symbol")["usd_value"].sum().sort_values(ascending=False).head(10).reset_index()
fig2, ax2 = plt.subplots(figsize=(6, 3))
ax2.barh(top_usd["token.symbol"], top_usd["usd_value"], color='green')
ax2.invert_yaxis()
st.pyplot(fig2)
st.dataframe(top_usd)

# Hourly Transfer Heatmap
st.subheader("🕓 Hourly Transfer Heatmap")
heatmap_df = df_filtered.groupby(['token.symbol', 'hour'])['transaction_hash'].count().unstack().fillna(0)
fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.heatmap(heatmap_df, cmap="Blues", linewidths=0.5, ax=ax3)
ax3.set_title("Transactions per Hour per Token")
st.pyplot(fig3)

# Rolling 7-day average volume
st.subheader("📅 7-Day Rolling Average Volume")
df_volume = df_filtered.groupby(['date', 'token.symbol'])['normalized_value'].sum().reset_index()
df_volume['rolling_avg'] = df_volume.groupby("token.symbol")["normalized_value"].transform(lambda x: x.rolling(7, 1).mean())
fig4, ax4 = plt.subplots(figsize=(10, 4))
for token in df_volume['token.symbol'].unique():
    subset = df_volume[df_volume['token.symbol'] == token]
    ax4.plot(subset['date'], subset['rolling_avg'], marker='o', label=token)
ax4.legend(fontsize=6)
ax4.tick_params(axis='x', labelrotation=45)
st.pyplot(fig4)

# Spike Detection (above 95th percentile)
st.subheader("🚨 Anomaly Detection: High-Value Transfers")
threshold = df_filtered['normalized_value'].quantile(0.95)
spikes = df_filtered[df_filtered['normalized_value'] > threshold]
st.dataframe(spikes[['timestamp', 'token.symbol', 'type', 'normalized_value', 'usd_value']].sort_values(by='normalized_value', ascending=False))

# Download section
st.subheader("⬇️ Download Insight Data")
csv = df_filtered.to_csv(index=False)
st.download_button("Download Filtered Data (CSV)", data=csv, file_name="filtered_token_data.csv", mime="text/csv")

st.markdown("---")
st.markdown("Made with ❤️ by Qenehelo Matjama | Advanced Dashboard")
