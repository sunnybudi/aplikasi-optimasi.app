import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi - Kendala Ganda", layout="wide")
st.title("🏭 Optimasi Produksi dengan Kendala Waktu, Bahan Baku, dan Tenaga Kerja")

st.markdown("""
Aplikasi ini membantu menentukan kombinasi produksi optimal untuk **memaksimalkan keuntungan** dengan mempertimbangkan tiga kendala utama:
- Jam kerja
- Bahan baku
- Tenaga kerja

### Fungsi Objektif:
\\[
\\text{Maximize } Z = \\sum_{i=1}^{n} c_i X_i = c_1 X_1 + c_2 X_2 + \\dots + c_n X_n
\\]
""")

# Jumlah produk
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
time_per_unit = []
material_per_unit = []
labor_per_unit = []

st.header("📦 Input Data Produk")
for i in range(num_products):
    st.subheader(f"Produk {i+1}")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit", value=10.0, key=f"profit_{i}")
    with col3:
        time = st.number_input(f"Jam Kerja/unit", value=1.0, key=f"time_{i}")
    with col4:
        material = st.number_input(f"Bahan Baku/unit", value=1.0, key=f"material_{i}")
    with col5:
        labor = st.number_input(f"Tenaga Kerja/unit", value=1.0, key=f"labor_{i}")

    product_names.append(name)
    profits.append(profit)
    time_per_unit.append(time)
    material_per_unit.append(material)
    labor_per_unit.append(labor)

# Input batas sumber daya
st.header("⚙️ Batasan Total Sumber Daya")
col_a, col_b, col_c = st.columns(3)
max_time = col_a.number_input("Total Jam Kerja Tersedia", value=100.0)
max_material = col_b.number_input("Total Bahan Baku Tersedia", value=100.0)
max_labor = col_c.number_input("Total Tenaga Kerja Tersedia", value=100.0)

# Tampilkan fungsi objektif & kendala
st.header("🧮 Fungsi Objektif dan Kendala")

obj_func = "Z = " + " + ".join([f"{profits[i]}X_{{{i+1}}}" for i in range(num_products)])
st.latex(obj_func)

st.markdown("### Kendala:")
st.latex(
    r"\begin{aligned}"
    + f"&\\text{{Jam Kerja:}} {' + '.join([f'{time_per_unit[i]}X_{{{i+1}}}' for i in range(num_products)])} \\leq {max_time} \\\\"
    + f"&\\text{{Bahan Baku:}} {' + '.join([f'{material_per_unit[i]}X_{{{i+1}}}' for i in range(num_products)])} \\leq {max_material} \\\\"
    + f"&\\text{{Tenaga Kerja:}} {' + '.join([f'{labor_per_unit[i]}X_{{{i+1}}}' for i in range(num_products)])} \\leq {max_labor}"
    + r"\end{aligned}"
)

# Optimasi
c = [-p for p in profits]
A = [time_per_unit, material_per_unit, labor_per_unit]
b = [max_time, max_material, max_labor]
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

    # Visualisasi diagram batang
    st.subheader("📊 Visualisasi Produksi Optimal")
    fig, ax = plt.subplots()
    bars = ax.bar(product_names, produk_optimal, color="skyblue")
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.2f}", ha="center")
    ax.set_ylabel("Jumlah Produksi Optimal")
    ax.set_title("Kombinasi Produksi Optimal")
    st.pyplot(fig)
else:
    st.error("❌ Optimasi gagal. Periksa kembali input parameter atau sumber daya.")
