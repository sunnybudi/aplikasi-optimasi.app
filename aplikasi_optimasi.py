import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi - Mesin & Operator", layout="wide")
st.title("🔧 Optimasi Produksi - Jumlah Mesin & Operator per Produk")

st.markdown("""
Aplikasi ini menghitung penjualan, keuntungan, total mesin, dan total operator berdasarkan input produk.

## Rumus:
\\[
Z = c_1 X_1 + c_2 X_2 + \\dots + c_n X_n
\\]
\\[
\\text{Total Operator Dibutuhkan} = \\sum (\\text{Mesin Produk}_i \\times \\text{Operator per Mesin}_i)
\\]
\\[
\\text{Efisiensi} = \\frac{\\text{Total Keuntungan}}{\\text{Total Operator}}
\\]
""")

# Input jumlah produk
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

# Data input per produk
product_names, jumlah_produksi, harga_jual, laba_per_unit = [], [], [], []
mesin_digunakan, operator_per_mesin = [], []

st.subheader("📥 Input Data Produk")
for i in range(num_products):
    st.markdown(f"### Produk {i+1}")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"nama_{i}")
    with col2:
        qty = st.number_input("Jumlah Produksi", min_value=0, value=0, key=f"jumlah_{i}")
    with col3:
        harga = st.number_input("Harga Jual/unit", min_value=0, value=0, key=f"harga_{i}")
    with col4:
        laba = st.number_input("Keuntungan/unit", min_value=0, value=0, key=f"laba_{i}")
    with col5:
        mesin = st.number_input("Jumlah Mesin Digunakan", min_value=0, value=0, key=f"mesin_{i}")
    with col6:
        op_mesin = st.number_input(f"Operator per Mesin (Produk {i+1})", min_value=1, value=1, key=f"opmesin_{i}")

    product_names.append(name)
    jumlah_produksi.append(qty)
    harga_jual.append(harga)
    laba_per_unit.append(laba)
    mesin_digunakan.append(mesin)
    operator_per_mesin.append(op_mesin)

# Fungsi format rupiah
def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")

# Perhitungan
total_penjualan = [harga_jual[i] * jumlah_produksi[i] for i in range(num_products)]
total_keuntungan = [laba_per_unit[i] * jumlah_produksi[i] for i in range(num_products)]
biaya_unit = [harga_jual[i] - laba_per_unit[i] for i in range(num_products)]
total_biaya = [biaya_unit[i] * jumlah_produksi[i] for i in range(num_products)]
total_operator_per_produk = [mesin_digunakan[i] * operator_per_mesin[i] for i in range(num_products)]
efisiensi_per_produk = [total_keuntungan[i] / total_operator_per_produk[i] if total_operator_per_produk[i] > 0 else 0 for i in range(num_products)]

total_all_penjualan = sum(total_penjualan)
total_all_keuntungan = sum(total_keuntungan)
total_all_biaya = sum(total_biaya)
total_mesin = sum(mesin_digunakan)
total_operator = sum(total_operator_per_produk)

# Tabel hasil
st.subheader("📊 Ringkasan Perhitungan")
df = pd.DataFrame({
    "Produk": product_names,
    "Jumlah Produksi": jumlah_produksi,
    "Mesin Digunakan": mesin_digunakan,
    "Operator/Mesin": operator_per_mesin,
    "Total Operator": total_operator_per_produk,
    "Harga Jual/unit": harga_jual,
    "Keuntungan/unit": laba_per_unit,
    "Total Penjualan": total_penjualan,
    "Total Keuntungan": total_keuntungan,
    "Total Biaya Produksi": total_biaya,
    "Efisiensi (Rp/Operator)": efisiensi_per_produk
})
st.dataframe(df.style.format({
    "Total Penjualan": "Rp {:,.0f}",
    "Total Keuntungan": "Rp {:,.0f}",
    "Total Biaya Produksi": "Rp {:,.0f}",
    "Efisiensi (Rp/Operator)": "Rp {:,.0f}"
}))

# Ringkasan
st.markdown("### 💰 Total Ringkasan")
st.write(f"📦 Total Penjualan: {format_rupiah(total_all_penjualan)}")
st.write(f"💸 Total Biaya Produksi: {format_rupiah(total_all_biaya)}")
st.write(f"✅ Total Keuntungan Bersih: {format_rupiah(total_all_keuntungan)}")
st.write(f"🛠️ Total Mesin Digunakan: {total_mesin} unit")
st.write(f"👷 Total Operator Dibutuhkan: {total_operator} orang")

# Rekomendasi Produk Berdasarkan Efisiensi
st.subheader("📌 Rekomendasi Prioritas Produksi")
df_prioritas = pd.DataFrame({
    "Produk": product_names,
    "Efisiensi": efisiensi_per_produk,
    "Total Keuntungan": total_keuntungan
}).sort_values(by="Efisiensi", ascending=False).reset_index(drop=True)

produk_efisien = df_prioritas.iloc[0]["Produk"]
efisiensi_tertinggi = df_prioritas.iloc[0]["Efisiensi"]
st.success(f"✅ Produk yang paling efisien diproduksi: **{produk_efisien}** (Efisiensi: {format_rupiah(efisiensi_tertinggi)} per operator)")

# Grafik (tanpa total operator, ditambah garis total penjualan semua produk)
st.subheader("📊 Diagram Perbandingan")
x_pos = np.arange(len(product_names))
width = 0.35
fig, ax = plt.subplots()

bar1 = ax.bar(x_pos - width/2, total_keuntungan, width, label='Keuntungan', color='skyblue')
bar2 = ax.bar(x_pos + width/2, total_penjualan, width, label='Penjualan', color='lightgreen')

# Garis total penjualan semua produk
total_line = ax.axhline(total_all_penjualan, color='red', linestyle='--', linewidth=2, label='Total Penjualan Semua Produk')

# Label batang
max_val = max(total_penjualan + total_keuntungan) if total_penjualan else 0
ax.set_ylim(0, max_val * 1.3)
for bars in [bar1, bar2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                height + 0.03 * max_val,
                f"{int(height):,}".replace(",", "."),
                ha='center', va='bottom', fontsize=9)

# Label garis
ax.text(len(product_names) - 0.5, total_all_penjualan + 0.02 * max_val,
        f"Total Semua Produk: {int(total_all_penjualan):,}".replace(",", "."),
        color='red', ha='right', fontsize=10, fontweight='bold')

ax.set_xticks(x_pos)
ax.set_xticklabels(product_names)
ax.set_ylabel("Nilai (Rupiah)")
ax.set_title("Perbandingan Penjualan dan Keuntungan per Produk")
ax.legend()
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
st.pyplot(fig)
