import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi Mahasiswa", layout="wide")
st.title("📈 Optimasi Produksi Multi-Produk")
st.markdown("""
Aplikasi ini digunakan untuk **memaksimalkan keuntungan** dari produksi dua atau lebih produk, dengan mempertimbangkan keterbatasan sumber daya seperti waktu, bahan baku, atau tenaga kerja.

### Rumus Fungsi Objektif:
\[
Z = c_1X_1 + c_2X_2 + \dots + c_nX_n
\]
dengan kendala:
\[
a_1X_1 + a_2X_2 + \dots + a_nX_n \leq R
\]
""")

# Input jumlah produk
st.sidebar.header("📦 Input Jumlah Produk")
num_products = st.sidebar.number_input("Jumlah Produk", min_value=2, value=2, step=1)

# Input parameter produk
st.sidebar.header("📥 Input Data Produk")
product_names = []
profits = []
resource_per_unit = []

for i in range(num_products):
    st.sidebar.subheader(f"Produk {i+1}")
    name = st.sidebar.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    profit = st.sidebar.number_input(f"Keuntungan/unit {name}", value=10.0, step=1.0, key=f"profit_{i}")
    usage = st.sidebar.number_input(f"Sumber Daya/unit {name}", value=1.0, step=1.0, key=f"usage_{i}")
    
    product_names.append(name)
    profits.append(profit)
    resource_per_unit.append(usage)

# Input total sumber daya
st.sidebar.header("⚙️ Total Sumber Daya")
total_resource = st.sidebar.number_input("Total Sumber Daya Tersedia", value=100.0, step=1.0)

# Fungsi objektif dan kendala
c = [-p for p in profits]  # Negatif karena linprog = minimisasi
A = [resource_per_unit]
b = [total_resource]
bounds = [(0, None)] * num_products

# Solusi optimasi
result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

st.header("📊 Hasil Optimasi Produksi")
if result.success:
    produk_optimal = np.round(result.x, 2)
    keuntungan_total = -result.fun

    df_hasil = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Produksi Optimal": produk_optimal,
        "Keuntungan/unit": profits,
        "Total Keuntungan": np.round(produk_optimal * profits, 2)
    })

    st.dataframe(df_hasil)
    st.success(f"💰 Total Keuntungan Maksimum: Rp {keuntungan_total:,.2f}")

    # Visualisasi batang
    st.subheader("📉 Visualisasi Produksi Optimal")
    fig, ax = plt.subplots()
    ax.bar(product_names, produk_optimal, color='skyblue')
    ax.set_ylabel("Jumlah Produksi")
    ax.set_title("Produksi Optimal per Produk")
    for i, v in enumerate(produk_optimal):
        ax.text(i, v + 0.5, f"{v:.2f}", ha='center')
    st.pyplot(fig)

    # Visualisasi area feasible (jika hanya 2 produk)
    if num_products == 2:
        st.subheader("📐 Visualisasi Area Feasible (2 Produk)")
        x_vals = np.linspace(0, total_resource / resource_per_unit[0], 200)
        y_vals = (total_resource - resource_per_unit[0] * x_vals) / resource_per_unit[1]

        fig2, ax2 = plt.subplots()
        ax2.plot(x_vals, y_vals, label="Kendala Sumber Daya", color='orange')
        ax2.fill_between(x_vals, 0, y_vals, where=(y_vals >= 0), color='gray', alpha=0.3)
        ax2.plot(produk_optimal[0], produk_optimal[1], 'ro', label="Solusi Optimal")
        ax2.set_xlabel(product_names[0])
        ax2.set_ylabel(product_names[1])
        ax2.set_title("Area Feasible dan Solusi Optimal")
        ax2.legend()
        st.pyplot(fig2)
else:
    st.error("❌ Optimasi gagal. Coba periksa kembali input Anda.")
