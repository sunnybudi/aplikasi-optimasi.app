import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi Tanpa Kendala", layout="wide")
st.title("💼 Optimasi Produksi (Tanpa Batasan Sumber Daya)")

st.markdown(r"""
### 🎯 Fungsi Objektif:
$$
\text{Maksimalkan: } Z = \sum_{i=1}^{n} p_i x_i
$$

Tanpa kendala (sumber daya tidak dibatasi), sistem menyarankan produksi maksimal berdasarkan produk dengan keuntungan tertinggi.
""")

# -------------------------
# Input Produk
# -------------------------
st.header("1️⃣ Input Data Produk")

num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []

for i in range(num_products):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit ({name})", value=10.0, step=1.0, key=f"profit_{i}")

    product_names.append(name)
    profits.append(profit)

# -------------------------
# Hasil (Tanpa Kendala)
# -------------------------
st.header("2️⃣ Hasil Optimasi (Tanpa Kendala)")

# Cek apakah semua input valid
if all(p > 0 for p in profits):
    max_profit = max(profits)
    max_index = profits.index(max_profit)
    optimal_product = product_names[max_index]

    st.success(f"✅ Produk dengan keuntungan tertinggi adalah **{optimal_product}**")
    st.markdown(f"👉 Maka, untuk memaksimalkan keuntungan **produksi harus difokuskan pada produk tersebut.**")

    # Tabel hasil
    df = pd.DataFrame({
        "Produk": product_names,
        "Keuntungan/unit": profits
    }).sort_values(by="Keuntungan/unit", ascending=False)

    st.dataframe(df)

    # Grafik batang keuntungan
    st.subheader("📊 Grafik Keuntungan per Produk")
    fig, ax = plt.subplots()
    bars = ax.bar(product_names, profits, color='mediumseagreen')

    for bar, val in zip(bars, profits):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5, f'{val:,.2f}', ha='center', va='bottom')

    ax.set_ylabel("Keuntungan per Unit")
    ax.set_title("Perbandingan Keuntungan per Produk")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
    ax.grid(True, axis='y', linestyle='--', alpha=0.4)
    st.pyplot(fig)

else:
    st.info("🔄 Masukkan semua keuntungan produk (harus > 0) untuk menampilkan hasil optimasi.")
