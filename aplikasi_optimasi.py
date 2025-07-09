import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("📦 Optimasi Produksi dengan Kendala Waktu, Bahan Baku, dan Tenaga Kerja")

st.markdown("""
Aplikasi ini menentukan kombinasi produksi optimal untuk memaksimalkan keuntungan berdasarkan batasan waktu, bahan baku, dan tenaga kerja.

### Fungsi Objektif:
\[
\text{Maximize } Z = c_1X_1 + c_2X_2 + \dots + c_nX_n
\]

### Kendala:
\[
\sum (a_{ij} X_j) \leq b_i \quad \text{untuk tiap sumber daya } i
\]
""")

# ------------------------------
# Input jumlah produk
# ------------------------------
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
time_per_unit = []
material_per_unit = []
labor_per_unit = []

st.header("📥 Input Data Produk")
for i in range(num_products):
    st.subheader(f"Produk {i+1}")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit {name}", value=10.0, key=f"profit_{i}")
    with col3:
        time = st.number_input(f"Jam Kerja/unit {name}", value=1.0, key=f"time_{i}")
    with col4:
        material = st.number_input(f"Bahan Baku/unit {name}", value=1.0, key=f"material_{i}")
    with col5:
        labor = st.number_input(f"Tenaga Kerja/unit {name}", value=1.0, key=f"labor_{i}")

    product_names.append(name)
    profits.append(profit)
    time_per_unit.append(time)
    material_per_unit.append(material)
    labor_per_unit.append(labor)

# ------------------------------
# Input batasan sumber daya
# ------------------------------
st.header("⚙️ Batasan Sumber Daya")
col1, col2, col3 = st.columns(3)
with col1:
    max_time = st.number_input("Total Jam Kerja Tersedia", value=100.0)
with col2:
    max_material = st.number_input("Total Bahan Baku Tersedia", value=100.0)
with col3:
    max_labor = st.number_input("Total Tenaga Kerja Tersedia", value=100.0)

# ------------------------------
# Perhitungan Optimasi
# ------------------------------
st.header("🧮 Hasil Perhitungan")

# Fungsi objektif
c = [-p for p in profits]

# Matriks kendala (A) dan batasannya (b)
A = [
    time_per_unit,
    material_per_unit,
    labor_per_unit
]
b = [max_time, max_material, max_labor]
bounds = [(0, None) for _ in range(num_products)]

# Optimasi
result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

if result.success:
    produk_optimal = np.round(result.x, 2)
    keuntungan_total = -result.fun

    df_hasil = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Produksi Optimal": produk_optimal,
        "Keuntungan/Unit": profits,
        "Total Keuntungan": np.round(np.multiply(produk_optimal, profits), 2)
    })

    st.success("✅ Solusi optimal ditemukan!")
    st.dataframe(df_hasil)
    st.subheader(f"💰 Total Keuntungan Maksimum: Rp {keuntungan_total:,.2f}")

    # Visualisasi diagram batang
    st.subheader("📊 Visualisasi Solusi Optimal")
    fig, ax = plt.subplots(figsize=(8, 4))
    bar = ax.bar(product_names, produk_optimal, color='skyblue')
    ax.set_ylabel("Jumlah Produksi Optimal")
    ax.set_title("Kombinasi Produksi Optimal")
    for bar_ in bar:
        height = bar_.get_height()
        ax.text(bar_.get_x() + bar_.get_width()/2, height + 0.5, f"{height:.2f}", ha='center')
    st.pyplot(fig)
else:
    st.error("❌ Optimasi gagal. Periksa kembali input sumber daya atau parameter produk.")
