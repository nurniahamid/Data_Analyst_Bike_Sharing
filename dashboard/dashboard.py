import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")  
sns.set(style="darkgrid")

@st.cache_data
def load_data():
    df = pd.read_csv("all_data.csv")
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load_data()

st.sidebar.header("🔍 Filter Data")

min_date = df["dteday"].min().date()
max_date = df["dteday"].max().date()
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

season_dict = {0: "Spring", 1: "Summer", 2: "Fall", 3: "Winter"}
selected_season = st.sidebar.selectbox("Pilih Musim", ["Semua"] + list(season_dict.values()))

weather_dict = {0: "Clear", 1: "Cloudy", 2: "Rainy", 3: "Snowy"}
selected_weather = st.sidebar.selectbox("Pilih Cuaca", ["Semua"] + list(weather_dict.values()))

hour_options = ["Semua"] + list(range(24))
selected_hours = st.sidebar.multiselect("Pilih Jam", hour_options, default=["Semua"])

if "Semua" in selected_hours:
    selected_hours = list(range(24))

st.sidebar.markdown("---")
st.sidebar.info("Gunakan filter di atas untuk menganalisis pola penyewaan sepeda.")

filtered_df = df[
    (df["dteday"].dt.date.between(date_range[0], date_range[1])) & 
    ((df["season_hour"].map(season_dict) == selected_season) if selected_season != "Semua" else True) & 
    ((df["weathersit_hour"].map(weather_dict) == selected_weather) if selected_weather != "Semua" else True) & 
    (df["hr"].isin(selected_hours))
]

avg_rentals = filtered_df["cnt_hourly"].mean()
max_rental_hour = filtered_df.loc[filtered_df["cnt_hourly"].idxmax(), "hr"] if not filtered_df.empty else None
min_rental_hour = filtered_df.loc[filtered_df["cnt_hourly"].idxmin(), "hr"] if not filtered_df.empty else None

st.title("🚴 Bike Sharing Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis pola penyewaan sepeda berdasarkan berbagai faktor.")

col1, col2, col3 = st.columns(3)
col1.metric("📊 Rata-rata Penyewaan per Jam", f"{avg_rentals:.2f} 🚲")
col2.metric("🔝 Jam dengan Penyewaan Tertinggi", f"{max_rental_hour}:00 🕒")
col3.metric("🔻 Jam dengan Penyewaan Terendah", f"{min_rental_hour}:00 🕒")

st.subheader("Tren Peminjaman Sepeda Berdasarkan Jam")

fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=filtered_df.groupby("hr")["cnt_hourly"].mean().index, 
             y=filtered_df.groupby("hr")["cnt_hourly"].mean().values, 
             marker="o", color="steelblue", ax=ax)  # Warna utama: biru
ax.set_xticks(range(24))
ax.set_title("Tren Peminjaman Sepeda Berdasarkan Jam")
ax.set_xlabel("Jam dalam Sehari")
ax.set_ylabel("Rata-rata Peminjaman Sepeda")
ax.grid()

st.pyplot(fig)

st.subheader("Peminjaman Sepeda Berdasarkan Musim dan Cuaca")

col1, col2 = st.columns(2)

with col1:
    st.write("### Berdasarkan Musim")
    season_rentals = filtered_df.groupby("season_hour")["cnt_hourly"].mean()
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    sns.barplot(x=season_rentals.index, y=season_rentals.values, color="steelblue", ax=ax1)  # Warna seragam biru
    ax1.set_xticklabels(["Spring", "Summer", "Fall", "Winter"])
    ax1.set_xlabel("Musim")
    ax1.set_ylabel("Rata-rata Peminjaman")
    st.pyplot(fig1)

with col2:
    st.write("### Berdasarkan Cuaca")
    weather_rentals = filtered_df.groupby("weathersit_hour")["cnt_hourly"].mean()
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    sns.barplot(x=weather_rentals.index, y=weather_rentals.values, color="steelblue", ax=ax2)  # Warna seragam biru
    ax2.set_xticklabels(["Cerah", "Mendung", "Hujan", "Salju"])
    ax2.set_xlabel("Cuaca")
    ax2.set_ylabel("Rata-rata Peminjaman")
    st.pyplot(fig2)

st.subheader("🔍 Scatterplot Analisis Penyewaan Sepeda")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

sns.scatterplot(ax=axes[0], x=df["temp_day"], y=df["cnt_hourly"], alpha=0.5, color="steelblue")
axes[0].set_title("Peminjaman Sepeda vs Suhu")
axes[0].set_xlabel("Suhu (Normalized)")
axes[0].set_ylabel("Jumlah Peminjaman")

sns.scatterplot(ax=axes[1], x=df["hum_day"], y=df["cnt_hourly"], alpha=0.5, color="steelblue")
axes[1].set_title("Peminjaman Sepeda vs Kelembapan")
axes[1].set_xlabel("Kelembapan (Normalized)")

sns.scatterplot(ax=axes[2], x=df["windspeed_day"], y=df["cnt_hourly"], alpha=0.5, color="steelblue")
axes[2].set_title("Peminjaman Sepeda vs Kecepatan Angin")
axes[2].set_xlabel("Kecepatan Angin (Normalized)")

plt.tight_layout()
st.pyplot(fig)

st.subheader("📊 Korelasi Antara Cuaca dan Penyewaan Sepeda")
correlation_matrix = df[["cnt_hourly", "temp_day", "hum_day", "windspeed_day"]].corr()

fig_corr, ax_corr = plt.subplots(figsize=(8, 5))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_corr)  # Warna coolwarm
ax_corr.set_title("Heatmap Korelasi")
st.pyplot(fig_corr)

st.subheader("📊 Tren Penyewaan Sepeda Harian")

fig_trend, ax_trend = plt.subplots(figsize=(12, 6))
ax_trend.plot(filtered_df["dteday"], filtered_df["cnt_hourly"], label="Total Peminjaman", color="blue", alpha=0.7)
ax_trend.set_xlabel("Tanggal")
ax_trend.set_ylabel("Total Penyewaan")
ax_trend.set_title("Tren Penyewaan Sepeda Harian")
ax_trend.legend()
ax_trend.grid()

st.pyplot(fig_trend)

st.subheader("📊 Moving Average Penyewaan Sepeda")

filtered_df["MA_7"] = filtered_df["cnt_hourly"].rolling(window=7).mean()
filtered_df["MA_30"] = filtered_df["cnt_hourly"].rolling(window=30).mean()

fig_ma, ax_ma = plt.subplots(figsize=(12, 6))
ax_ma.plot(filtered_df["dteday"], filtered_df["cnt_hourly"], label="Total Peminjaman", color="blue", alpha=0.5)
ax_ma.plot(filtered_df["dteday"], filtered_df["MA_7"], label="Moving Average 7 Hari", color="red")
ax_ma.plot(filtered_df["dteday"], filtered_df["MA_30"], label="Moving Average 30 Hari", color="green")
ax_ma.set_xlabel("Tanggal")
ax_ma.set_ylabel("Total Penyewaan")
ax_ma.set_title("Moving Average Penyewaan Sepeda")
ax_ma.legend()
ax_ma.grid()

st.pyplot(fig_ma)

st.subheader("🔍 Decomposition Analysis: Trend, Seasonality & Residual")

decomposition = seasonal_decompose(filtered_df["cnt_hourly"], model="additive", period=30)

fig_decomp, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

axes[0].plot(filtered_df["dteday"], filtered_df["cnt_hourly"], label="Original", color="blue")
axes[0].legend()
axes[0].set_title("Original Data")

axes[1].plot(filtered_df["dteday"], decomposition.trend, label="Trend", color="red")
axes[1].legend()
axes[1].set_title("Trend")

axes[2].plot(filtered_df["dteday"], decomposition.seasonal, label="Seasonality", color="green")
axes[2].legend()
axes[2].set_title("Seasonality")

axes[3].plot(filtered_df["dteday"], decomposition.resid, label="Residual", color="black")
axes[3].legend()
axes[3].set_title("Residual")

plt.tight_layout()
st.pyplot(fig_decomp)

st.success("Dashboard Interaktif By Nurnia Hamid! 🚀")
