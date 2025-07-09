import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("📦 Optimasi Produksi - Maksimalkan Keuntungan")

st.markdown("""
Aplikasi ini membantu menentukan kombinasi produk optimal untuk memaksimalkan keuntungan berdasarkan jumlah tenaga kerja (operator) sebagai kendala utama.

### Fungsi Objektif:
\[
Z = c_1 X_1 + c_2 X_2 + \dots + c_n X_n
\]

Dengan kendala:
\[
a_1 X_1 + a_2 X_2 + \dots + a_n X_n \leq B
\]
di mana:
- \( c_i \): keuntungan per unit produk ke-i  
- \( a_i \): operator per unit produk ke-i  
- \( B \): total operator tersedia  
""")

# ===============================
# 📌 Input Produk Dinamis
# ===============================
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
tenaga_per_unit = []

st.subheader("🔢 Input Data Produk")
for i in range(num_products):
    st.markdown(f"**Produk {i+1}**")
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

# ===============================
# 📌 Input Kendala: Total Operator
# ===============================
st.subheader("👷 Jumlah Operator Tersedia")
total_operator = st.number_input("Total Jam Kerja Operator", value=100.0, step=1.0)

# ===============================
# 🚀 Optimasi Produksi
# ===============================
st.subheader("🧮 Hasil Optimasi Produksi")

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
        "Jumlah Optimal Produksi": produk_optimal,
        "Keuntungan per Unit": profits,
        "Total Keuntungan": np.round(np.multiply(produk_optimal, profits), 2),
        "Total Jam Operator": np.round(np.multiply(produk_optimal, tenaga_per_unit), 2)
    })

    st.success("✅ Solusi optimal ditemukan!")
    st.dataframe(df_hasil)
    st.subheader(f"💰 Total Keuntungan Maksimum: Rp {keuntungan_total:,.0f}")

    # ===============================
    # 📘 Rincian Setiap Produk
    # ===============================
    st.subheader("📘 Rincian Hasil per Produk")
    for i in range(num_products):
        st.markdown(f"""
        **{product_names[i]}**
        - Jumlah Produksi Optimal: `{produk_optimal[i]:.2f}` unit
        - Keuntungan per unit: `Rp {profits[i]:,.0f}`
        - Total Keuntungan: `Rp {produk_optimal[i] * profits[i]:,.0f}`
        - Penggunaan Operator: `{produk_optimal[i] * tenaga_per_unit[i]:.2f}` jam
        """)

    # ===============================
    # 📊 Grafik Batang
    # ===============================
    st.subheader("📊 Visualisasi Produksi Optimal")

    fig, ax = plt.subplots()
    bars = ax.bar(product_names, produk_optimal, color="skyblue")
    ax.set_ylabel("Jumlah Produksi Optimal")
    ax.set_title("Grafik Produksi Optimal")

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.2f}', ha='center', va='bottom')

    st.pyplot(fig)

else:
    st.error("❌ Optimasi gagal. Periksa input dan batasan sumber daya.")
