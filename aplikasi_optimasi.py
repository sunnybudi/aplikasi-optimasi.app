import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi Multikendala", layout="wide")
st.title("🏭 Optimasi Produksi dengan Kendala Waktu, Bahan Baku, dan Tenaga Kerja")

st.markdown("""
Aplikasi ini membantu memaksimalkan keuntungan dari produksi dua atau lebih produk dengan memperhitungkan kendala:
- Waktu kerja
- Bahan baku
- Tenaga kerja

### Fungsi Objektif:
\[
\text{Maximize } Z = \sum_{i=1}^{n} c_i X_i
\]
""")

num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
time_per_unit = []
material_per_unit = []
labor_per_unit = []

st.header("📦 Input Parameter Tiap Produk")
for i in range(num_products):
    st.subheader(f"Produk {i+1}")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit {name}", value=10.0, key=f"profit_{i}")
    with col3:
        t = st.number_input(f"Jam kerja/unit {name}", value=1.0, key=f"time_{i}")
    with col4:
        m = st.number_input(f"Bahan baku/unit {name}", value=1.0, key=f"material_{i}")
    with col5:
        l = st.number_input(f"Tenaga kerja/unit {name}", value=1.0, key=f"labor_{i}")

    product_names.append(name)
    profits.append(profit)
    time_per_unit.append(t)
    material_per_unit.append(m)
    labor_per_unit.append(l)

st.header("🔧 Total Sumber Daya Tersedia")
max_time = st.number_input("Total Jam Kerja Tersedia", value=100.0)
max_material = st.number_input("Total Bahan Baku Tersedia", value=80.0)
max_labor = st.number_input("Total Tenaga Kerja Tersedia", value=90.0)

st.header("🧮 Fungsi Objektif dan Kendala")
st.markdown("### Fungsi Objektif")
st.latex("Z = " + " + ".join([f"{profits[i]}X_{{{i+1}}}" for i in range(num_products)]))

st.markdown("### Kendala")
st.latex("""
\begin{aligned}
&\text{Jam Kerja:} &&""" + " + ".join([f"{time_per_unit[i]}X_{{{i+1}}}" for i in range(num_products)]) + f" \leq {max_time} \\
&\text{Bahan Baku:} &&" + " + ".join([f"{material_per_unit[i]}X_{{{i+1}}}" for i in range(num_products)]) + f" \leq {max_material} \\
&\text{Tenaga Kerja:} &&" + " + ".join([f"{labor_per_unit[i]}X_{{{i+1}}}" for i in range(num_products)]) + f" \leq {max_labor}
\end{aligned}
"""
)

# Optimasi Linear Programming
c = [-p for p in profits]
A = [time_per_unit, material_per_unit, labor_per_unit]
b = [max_time, max_material, max_labor]
bounds = [(0, None)] * num_products

result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

if result.success:
    jumlah_optimal = np.round(result.x, 2)
    keuntungan_total = -result.fun

    df = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Optimal": jumlah_optimal,
        "Keuntungan/Unit": profits,
        "Total Keuntungan": np.round(np.multiply(jumlah_optimal, profits), 2)
    })

    st.success("✅ Solusi optimal ditemukan!")
    st.dataframe(df)
    st.subheader(f"💰 Total Keuntungan Maksimum: Rp {keuntungan_total:,.2f}")

    # Visualisasi
    st.subheader("📊 Visualisasi Produksi Optimal")
    fig, ax = plt.subplots()
    bars = ax.bar(product_names, jumlah_optimal, color="lightblue")
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.3, f"{height}", ha='center')
    ax.set_ylabel("Jumlah Produksi")
    ax.set_title("Hasil Produksi Optimal Tiap Produk")
    st.pyplot(fig)
else:
    st.error("❌ Optimasi gagal. Coba periksa input dan batasan sumber daya.")
