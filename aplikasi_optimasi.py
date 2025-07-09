import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi Dinamis", layout="wide")
st.title("📈 Optimasi Produksi - Maksimalkan Keuntungan (Multi Produk)")

st.markdown("""
Aplikasi ini membantu menentukan kombinasi produksi optimal untuk memaksimalkan keuntungan dari **dua atau lebih produk**.

### Rumus Umum:
\\[
Z = \\sum_{i=1}^{n} c_i X_i = c_1 X_1 + c_2 X_2 + \\dots + c_n X_n
\\]
""")

# ==============================
# Input Jumlah Produk dan Data
# ==============================
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
quantities = []
profits = []
prices = []

st.header("📦 Input Data Tiap Produk")

for i in range(num_products):
    st.subheader(f"Produk {i+1}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        qty = st.number_input(f"Jumlah Produksi {name}", value=0, step=1, key=f"qty_{i}")
    with col3:
        profit = st.number_input(f"Keuntungan/unit {name}", value=0, step=1, key=f"profit_{i}")
    with col4:
        price = st.number_input(f"Harga Jual {name}", value=0, step=1, key=f"price_{i}")
    
    product_names.append(name)
    quantities.append(qty)
    profits.append(profit)
    prices.append(price)

# ==============================
# Perhitungan Total Keuntungan & Penjualan
# ==============================

total_profit_per_product = [quantities[i] * profits[i] for i in range(num_products)]
total_sales_per_product = [quantities[i] * prices[i] for i in range(num_products)]
total_profit = sum(total_profit_per_product)
total_sales = sum(total_sales_per_product)

# ==============================
# Tampilkan Fungsi Z
# ==============================
st.header("🧮 Fungsi Objektif dan Total Keuntungan")

latex_str = "Z = " + " + ".join([f"{profits[i]}\\times{quantities[i]}" for i in range(num_products)])
latex_str += f" = {total_profit}"
st.latex(latex_str)

# ==============================
# Tabel Ringkasan
# ==============================
st.header("📊 Ringkasan Produksi")

df = pd.DataFrame({
    "Produk": product_names,
    "Jumlah Produksi": quantities,
    "Keuntungan/Unit": profits,
    "Total Keuntungan": total_profit_per_product,
    "Harga Jual": prices,
    "Total Penjualan": total_sales_per_product
})

st.dataframe(df, use_container_width=True)

# ==============================
# Visualisasi: Grafik Batang
# ==============================
st.subheader("📈 Grafik Perbandingan Total Penjualan dan Keuntungan")

kategori = product_names + ["Total"]
penjualan = total_sales_per_product + [total_sales]
keuntungan = total_profit_per_product + [total_profit]

x_pos = np.arange(len(kategori))
width = 0.35
fig, ax = plt.subplots(figsize=(10, 5))

bar1 = ax.bar(x_pos - width/2, keuntungan, width=width, color='skyblue', label='Keuntungan')
bar2 = ax.bar(x_pos + width/2, penjualan, width=width, color='lightgreen', label='Penjualan')

max_val = max(penjualan + keuntungan)
ax.set_ylim(0, max_val * 1.2)

for bars in [bar1, bar2]:
    for bar in bars:
        val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, val + max_val * 0.03, f"{val:,.0f}".replace(",", "."), 
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel("Rupiah")
ax.set_title("Perbandingan Penjualan dan Keuntungan")
ax.set_xticks(x_pos)
ax.set_xticklabels(kategori)
ax.legend()
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))

st.pyplot(fig)
