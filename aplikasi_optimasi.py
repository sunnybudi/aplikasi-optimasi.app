import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("📦 Optimasi Produksi - Maksimalkan Keuntungan")

st.markdown("""
Aplikasi ini menghitung kombinasi produksi optimal dari beberapa produk berdasarkan batasan sumber daya.

### Fungsi Objektif
\[
\text{Maximize } Z = c_1 X_1 + c_2 X_2 + \dots + c_n X_n
\]
Dengan kendala:
\[
a_1 X_1 + a_2 X_2 + \dots + a_n X_n \leq B
\]
""")

# Input jumlah produk
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
resources_used = []

st.header("📥 Input Produk")
for i in range(num_products):
    st.subheader(f"Produk {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit {name}", value=10.0, key=f"profit_{i}")
    with col3:
        resource = st.number_input(f"Sumber Daya/unit {name}", value=1.0, key=f"resource_{i}")

    product_names.append(name)
    profits.append(profit)
    resources_used.append(resource)

st.header("⚙️ Batasan Sumber Daya")
total_resource = st.number_input("Total Sumber Daya Tersedia", value=100.0, step=1.0)

# Tampilkan rumus
st.header("📐 Rumus Perhitungan")
objective_str = " + ".join([f"{profits[i]}×X_{{{i+1}}}" for i in range(num_products)])
constraint_str = " + ".join([f"{resources_used[i]}×X_{{{i+1}}}" for i in range(num_products)]) + f" ≤ {total_resource}"
st.latex(f"\\text{{Maximize }} Z = {objective_str}")
st.latex(constraint_str)

# Optimasi
c = [-p for p in profits]  # negative for maximization
A = [resources_used]
b = [total_resource]
bounds = [(0, None)] * num_products

result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

if result.x is not None:
    produk_optimal = np.round(result.x, 2)
    total_keuntungan = np.round(np.dot(produk_optimal, profits), 2)

    df_hasil = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Optimal Produksi": produk_optimal,
        "Keuntungan/unit": profits,
        "Total Keuntungan Produk": np.round(np.multiply(produk_optimal, profits), 2)
    })

    if result.success:
        st.success("✅ Solusi optimal ditemukan!")
    else:
        st.warning("⚠️ Solusi tidak optimal, berikut hasil pendekatan solver.")

    st.dataframe(df_hasil)
    st.subheader(f"💰 Total Keuntungan: Rp {total_keuntungan:,.2f}")

    # Grafik batang
    st.subheader("📊 Visualisasi Produksi")
    fig, ax = plt.subplots()
    bars = ax.bar(product_names, produk_optimal, color='skyblue')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.2f}", ha='center')

    ax.set_ylabel("Jumlah Produksi")
    ax.set_title("Produksi Optimal Tiap Produk")
    st.pyplot(fig)
else:
    st.error("❌ Optimasi gagal. Tidak ada solusi ditemukan.")
