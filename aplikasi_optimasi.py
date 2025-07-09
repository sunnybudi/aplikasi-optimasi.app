import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi - Maksimalkan Keuntungan", layout="wide")
st.title("📈 Optimasi Produksi - Maksimalkan Keuntungan")
st.markdown("""
Aplikasi ini membantu menentukan kombinasi produksi optimal untuk memaksimalkan keuntungan dengan mempertimbangkan batasan sumber daya (waktu, bahan baku, tenaga kerja).
""")

# Input jumlah produk
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
constraints = []

st.header("📦 Input Data Produk")
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
st.header("⚙️ Batasan Sumber Daya")
total_resource = st.number_input("Total Sumber Daya Tersedia", value=100.0, step=1.0)

# Tampilkan perhitungan awal
st.header("🧮 Proses Perhitungan")
st.markdown("### Fungsi Objektif")
obj_func = "Z = " + " + ".join([f"{profits[i]}×{product_names[i]}" for i in range(num_products)])
st.latex(obj_func)

st.markdown("### Kendala")
constraints_expr = " + ".join([f"{constraints[i]}×{product_names[i]}" for i in range(num_products)]) + f" \leq {total_resource}"
st.latex(constraints_expr)

# Optimasi langsung tanpa tombol
c = [-p for p in profits]
A = [constraints]
b = [total_resource]
bounds = [(0, None) for _ in range(num_products)]

result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

if result.success:
    produk_optimal = np.round(result.x, 2)
    keuntungan_total = -result.fun

    df_hasil = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Optimal": produk_optimal,
        "Keuntungan/Unit": profits,
        "Total Keuntungan": np.round(np.multiply(produk_optimal, profits), 2)
    })

    st.success("✅ Solusi optimal ditemukan!")
    st.dataframe(df_hasil)
    st.subheader(f"💰 Total Keuntungan Maksimum: Rp {keuntungan_total:,.2f}")

    # Grafik batang
    st.subheader("📊 Visualisasi Solusi Optimal")
    fig, ax = plt.subplots(figsize=(8, 4))
    bar1 = ax.bar(product_names, produk_optimal, color='skyblue')
    for bar in bar1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.2f}", ha='center')
    ax.set_ylabel("Jumlah Produksi Optimal")
    ax.set_title("Kombinasi Produksi Optimal")
    st.pyplot(fig)
else:
    st.error("❌ Optimasi gagal. Periksa kembali input sumber daya dan parameter produk.")
