import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("📈 Optimasi Produksi - Maksimalkan Keuntungan")

st.markdown("""
Aplikasi ini membantu menentukan kombinasi produksi optimal untuk memaksimalkan keuntungan berdasarkan batasan tenaga kerja (operator).

### Rumus Fungsi Objektif:
\[
Z = c_1 X + c_2 Y + \dots + c_n X_n
\]
""")

# Input jumlah produk
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
tenaga_per_unit = []

st.header("📦 Input Data Produk")
for i in range(num_products):
    st.subheader(f"Produk {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit {name}", value=10.0, key=f"profit_{i}")
    with col3:
        tenaga = st.number_input(f"Tenaga Kerja/unit {name}", value=1.0, key=f"tenaga_{i}")
    
    product_names.append(name)
    profits.append(profit)
    tenaga_per_unit.append(tenaga)

# Input total tenaga kerja
st.header("👷 Total Tenaga Kerja Tersedia")
total_operator = st.number_input("Jumlah Total Operator", value=100.0)

# Optimasi
c = [-p for p in profits]
A = [tenaga_per_unit]
b = [total_operator]
bounds = [(0, None) for _ in range(num_products)]

result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

if result.success:
    produk_optimal = np.round(result.x, 2)
    keuntungan_total = -result.fun

    df_hasil = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Optimal": produk_optimal,
        "Keuntungan/unit": profits,
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

    # Simulasi jika hanya satu produk diproduksi
    st.subheader("🔍 Perbandingan Jika Hanya Produksi Satu Produk Saja")
    simulasi_data = []

    for i in range(num_products):
        max_jumlah = total_operator / tenaga_per_unit[i] if tenaga_per_unit[i] != 0 else 0
        jumlah_produksi = np.floor(max_jumlah)
        total_untung = jumlah_produksi * profits[i]
        total_operator_pakai = jumlah_produksi * tenaga_per_unit[i]

        simulasi_data.append({
            "Produk": product_names[i],
            "Jumlah Jika Sendiri": jumlah_produksi,
            "Keuntungan Jika Sendiri": total_untung,
            "Operator Digunakan": total_operator_pakai
        })

    df_simulasi = pd.DataFrame(simulasi_data)
    st.dataframe(df_simulasi)

else:
    st.error("❌ Optimasi gagal. Periksa input.")
