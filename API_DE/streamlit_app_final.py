
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# === Load Data ===
@st.cache_data
def load_data():
    excel_path = "DE_Assesment_Results.xlsx"
    df_summary = pd.read_excel(excel_path, sheet_name="task3_summary_report")
    df_cleaned = pd.read_excel(excel_path, sheet_name="Total_cleaned_records")
    df_trend = pd.read_excel(excel_path, sheet_name="task4_volume_per_day", parse_dates=['date'])
    df_supply = pd.read_excel(excel_path, sheet_name="task4_cumulative_supply", parse_dates=['date'])
    df_top = pd.read_excel(excel_path, sheet_name="task4_top_tokens")
    return df_summary, df_cleaned, df_trend, df_supply, df_top

st.set_page_config(page_title="Token Analytics Dashboard", layout="wide")
st.title("📊 Token Distribution & Blockchain Trend Dashboard")

df_summary, df_cleaned, df_trend, df_supply, df_top = load_data()

# === Sidebar Filters ===
all_tokens = df_cleaned['token.symbol'].dropna().unique().tolist()
all_types = df_cleaned['type'].dropna().unique().tolist()
min_date = df_cleaned['timestamp'].min()
max_date = df_cleaned['timestamp'].max()
min_rate = float(df_cleaned['token.exchange_rate'].min())
max_rate = float(df_cleaned['token.exchange_rate'].max())

st.sidebar.header("🔍 Filter Transactions")
selected_token = st.sidebar.selectbox("Select Token Symbol", ["All"] + all_tokens)
selected_type = st.sidebar.selectbox("Select Transaction Type", ["All"] + all_types)
selected_date = st.sidebar.date_input("Filter by Date Range", [min_date, max_date])
rate_range = st.sidebar.slider("Token Exchange Rate", min_value=0.001, max_value=1.0, value=(min_rate, max_rate))

df_filtered = df_cleaned.copy()
if selected_token != "All":
    df_filtered = df_filtered[df_filtered['token.symbol'] == selected_token]
if selected_type != "All":
    df_filtered = df_filtered[df_filtered['type'] == selected_type]
df_filtered = df_filtered[
    (df_filtered['timestamp'].dt.date >= selected_date[0]) &
    (df_filtered['timestamp'].dt.date <= selected_date[1]) &
    (df_filtered['token.exchange_rate'] >= rate_range[0]) &
    (df_filtered['token.exchange_rate'] <= rate_range[1])
]

# === Summary Table ===
st.subheader("📦 Top Token Holders and Distribution Summary")
st.dataframe(df_summary.style.format({
    "Token Holding": "{:.6f}",
    "% of Total Holding": "{:.2f}%",
    "Tokens Sent": "{:.6f}",
    "% of Total Sent": "{:.2f}%",
    "Tokens Received": "{:.6f}",
    "% of Total Received": "{:.2f}%"
}))

# === Task 3 Charts ===
st.subheader("📈 Visual Breakdown by Address")
col1, col2, col3 = st.columns(3)

def labeled_barh(data, column, title, color):
    fig, ax = plt.subplots(figsize=(4, 2.5))  # Reduced figure size
    bars = ax.barh(data['address'], data[column], color=color)
    ax.set_xlabel(column)
    ax.set_title(title, fontsize=10)
    ax.tick_params(labelsize=8)
    ax.invert_yaxis()
    return fig

with col1:
    fig1 = labeled_barh(df_summary, "Token Holding", "Token Holdings", "green")
    st.pyplot(fig1)
    st.table(df_summary[['address', 'Token Holding']])  # Add data table below the graph

with col2:
    fig2 = labeled_barh(df_summary, "Tokens Sent", "Tokens Sent", "red")
    st.pyplot(fig2)
    st.table(df_summary[['address', 'Tokens Sent']])  # Add data table below the graph

with col3:
    fig3 = labeled_barh(df_summary, "Tokens Received", "Tokens Received", "blue")
    st.pyplot(fig3)
    st.table(df_summary[['address', 'Tokens Received']])  # Add data table below the graph

# === Task 4 Charts ===
st.subheader("📉 Task 4: Blockchain Activity Trends")
col4, col5 = st.columns(2)

with col4:
    st.markdown("##### 🔄 Daily Token Transfer Volume")
    df_t4 = df_trend.copy()
    if selected_token != "All":
        df_t4 = df_t4[df_t4['token'] == selected_token]
    fig4, ax4 = plt.subplots(figsize=(5, 2.5))  # Reduced figure size
    for token in df_t4['token'].unique():
        token_df = df_t4[df_t4['token'] == token]
        ax4.plot(token_df['date'], token_df['daily_volume'], marker='o', label=token)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax4.tick_params(axis='x', labelrotation=45, labelsize=8)
    ax4.legend(fontsize=7)
    st.pyplot(fig4)
    st.table(df_t4[['date', 'daily_volume']])  # Add data table below the graph

with col5:
    st.markdown("##### 📈 Cumulative Token Supply")
    df_sup = df_supply.copy()
    if selected_token != "All":
        df_sup = df_sup[df_sup['token.symbol'] == selected_token]
    fig5, ax5 = plt.subplots(figsize=(5, 2.5))  # Reduced figure size
    for token in df_sup['token.symbol'].unique():
        token_df = df_sup[df_sup['token.symbol'] == token]
        ax5.plot(token_df['date'], token_df['cumulative_supply'], marker='o', label=token)
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax5.tick_params(axis='x', labelrotation=45, labelsize=8)
    ax5.legend(fontsize=7)
    st.pyplot(fig5)
    st.table(df_sup[['date', 'cumulative_supply']])  # Add data table below the graph

# === Top Tokens
st.subheader("🏆 Most Transferred Tokens")
fig6, ax6 = plt.subplots(figsize=(5, 2.5))  # Reduced figure size
bars = ax6.barh(df_top['token.symbol'], df_top['total_transferred'], color='orange')
ax6.set_xlabel("Total Transferred")
ax6.set_ylabel("Token")
ax6.tick_params(labelsize=8)
ax6.invert_yaxis()
st.pyplot(fig6)
st.table(df_top[['token.symbol', 'total_transferred']])  # Add data table below the graph

# === Raw Cleaned Table
st.subheader("📄 Cleaned Token Transfer Records")
st.dataframe(df_filtered.reset_index(drop=True))


# === Additional Task 4 Insights ===
st.subheader("🚨 Additional Token Trend Insights")

# 1. Weekly & Monthly Aggregates
df_trend['week'] = pd.to_datetime(df_trend['date']).dt.to_period('W').dt.start_time
df_trend['month'] = pd.to_datetime(df_trend['date']).dt.to_period('M').dt.start_time

st.markdown("#### 📅 Weekly Aggregated Volume")
weekly_vol = df_trend.groupby(['week', 'token'])['daily_volume'].sum().reset_index()
fig_week, ax_week = plt.subplots(figsize=(5, 2.5))  # Reduced figure size
for token in weekly_vol['token'].unique():
    token_df = weekly_vol[weekly_vol['token'] == token]
    ax_week.plot(token_df['week'], token_df['daily_volume'], marker='o', label=token)
ax_week.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax_week.tick_params(axis='x', labelrotation=45, labelsize=8)
ax_week.legend(fontsize=7)
st.pyplot(fig_week)
st.table(weekly_vol[['week', 'daily_volume']])  # Add data table below the graph

st.markdown("#### 🗓 Monthly Aggregated Volume")
monthly_vol = df_trend.groupby(['month', 'token'])['daily_volume'].sum().reset_index()
fig_month, ax_month = plt.subplots(figsize=(5, 2.5))  # Reduced figure size
for token in monthly_vol['token'].unique():
    token_df = monthly_vol[monthly_vol['token'] == token]
    ax_month.plot(token_df['month'], token_df['daily_volume'], marker='o', label=token)
ax_month.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_month.tick_params(axis='x', labelrotation=45, labelsize=8)
ax_month.legend(fontsize=7)
st.pyplot(fig_month)
st.table(monthly_vol[['month', 'daily_volume']])  # Add data table below the graph

# 2. Spike Detection in Minting/Burning
st.markdown("#### 🔍 Spike Detection in Minting & Burning")
df_spike = df_cleaned.copy()
df_spike['date'] = df_spike['timestamp'].dt.date
mint_burn_spikes = df_spike[df_spike['type'].isin(['token_minting', 'token_burning'])]
spikes_summary = mint_burn_spikes.groupby(['date', 'token.symbol', 'type'])['normalized_value'].sum().reset_index()
pivot_spikes = spikes_summary.pivot(index=['date', 'token.symbol'], columns='type', values='normalized_value').fillna(0)
pivot_spikes.reset_index(inplace=True)
st.dataframe(pivot_spikes.sort_values(by=['date', 'token.symbol'], ascending=[False, True]).head(10))

# 3. Most Actively Traded Tokens
st.markdown("#### 📊 Most Actively Traded Tokens by Count")
most_active = df_cleaned[df_cleaned['type'] == 'token_transfer'].groupby('token.symbol')['transaction_hash'].count().reset_index()
most_active.columns = ['token.symbol', 'transaction_count']
most_active = most_active.sort_values(by='transaction_count', ascending=False).head(10)
fig_active, ax_active = plt.subplots(figsize=(5, 2.5))  # Reduced figure size
bars = ax_active.barh(most_active['token.symbol'], most_active['transaction_count'], color='purple')
ax_active.set_xlabel("Transaction Count")
ax_active.set_ylabel("Token")
ax_active.invert_yaxis()
st.pyplot(fig_active)
st.table(most_active[['token.symbol', 'transaction_count']])  # Add data table below the graph

st.markdown("---")
st.markdown("Made with ❤️ by Qenehelo Matjama")
