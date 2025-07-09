import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi - Semua Produk Ditampilkan", layout="wide")
st.title("📦 Optimasi Produksi dengan Semua Produk Ditampilkan")

st.markdown("""
Aplikasi ini menghitung jumlah produksi optimal untuk memaksimalkan keuntungan dengan tetap menampilkan semua data input per produk, termasuk jika jumlah optimalnya nol.

### Fungsi Objektif:
\\[
\\text{Maximize } Z = \\sum_{i=1}^{n} c_i X_i
\\]
""")

# Input jumlah produk
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
constraints = []

st.header("📥 Input Data Produk")
for i in range(num_products):
    st.subheader(f"Produk {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit {name}", value=10.0, key=f"profit_{i}")
    with col3:
        cons = st.number_input(f"Sumber Daya/unit {name}", value=1.0, key=f"cons_{i}")

    product_names.append(name)
    profits.append(profit)
    constraints.append(cons)

# Input total sumber daya tersedia
total_resource = st.number_input("Total Sumber Daya Tersedia", value=100.0, step=1.0)

# Tampilkan fungsi objektif & kendala
st.header("🧮 Fungsi Objektif & Kendala")
st.markdown("### Fungsi Objektif")
st.latex("Z = " + " + ".join([f"{profits[i]}X_{{{i+1}}}" for i in range(num_products)]))

st.markdown("### Kendala")
st.latex(" + ".join([f"{constraints[i]}X_{{{i+1}}}" for i in range(num_products)]) + f" \\leq {total_resource}")

# Optimasi
c = [-p for p in profits]
A = [constraints]
b = [total_resource]
bounds = [(0, None) for _ in range(num_products)]

result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
produk_optimal = np.round(result.x, 2) if result.success else [0]*num_products

# Perhitungan total per produk (berdasarkan hasil optimal atau tidak)
total_keuntungan = np.round(np.multiply(produk_optimal, profits), 2)
total_sumber_daya = np.round(np.multiply(produk_optimal, constraints), 2)

df_hasil = pd.DataFrame({
    "Produk": product_names,
    "Jumlah Optimal Produksi": produk_optimal,
    "Konsumsi Sumber Daya": total_sumber_daya,
    "Keuntungan/Unit": profits,
    "Total Keuntungan": total_keuntungan
})

st.header("📋 Hasil Perhitungan Semua Produk")
st.dataframe(df_hasil)

# Total keuntungan
if result.success:
    st.success(f"✅ Solusi Optimal Ditemukan | Total Keuntungan: Rp {np.sum(total_keuntungan):,.2f}")
else:
    st.warning("⚠️ Optimasi gagal. Menampilkan hasil default tanpa solusi optimal.")

# Grafik
st.subheader("📊 Grafik Jumlah Produksi Optimal per Produk")
fig, ax = plt.subplots(figsize=(8, 4))
bar = ax.bar(product_names, produk_optimal, color='skyblue')
for rect in bar:
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2, height + 0.5, f"{height:.2f}", ha='center')

ax.set_ylabel("Jumlah Produksi Optimal")
ax.set_title("Visualisasi Solusi Produksi Optimal")
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
st.pyplot(fig)
