import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi Dinamis", layout="wide")
st.title("📈 Optimasi Produksi - Fungsi Objektif Dinamis + Operator & Mesin")

st.markdown("""
Aplikasi ini menghitung total penjualan dan keuntungan dari beberapa produk dengan tambahan kendala jumlah mesin dan operator:

\[
\text{Total Operator Dibutuhkan} = \left( \sum_{i=1}^{n} Q_i \times M_i \right) \times \text{Operator per Mesin}
\]
""")

# Input jumlah produk
num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
jumlah_produksi = []
harga_jual = []
laba_per_unit = []
mesin_per_produk = []

st.subheader("📝 Input Data Produk")
for i in range(num_products):
    st.markdown(f"### Produk {i+1}")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"nama_{i}")
    with col2:
        qty = st.number_input(f"Jumlah Produksi", min_value=0, value=0, key=f"jumlah_{i}")
    with col3:
        harga = st.number_input(f"Harga Jual/unit", min_value=0, value=0, key=f"harga_{i}")
    with col4:
        laba = st.number_input(f"Keuntungan/unit", min_value=0, value=0, key=f"laba_{i}")
    with col5:
        mesin = st.number_input(f"Mesin/unit", min_value=0.0, value=1.0, key=f"mesin_{i}")

    product_names.append(name)
    jumlah_produksi.append(qty)
    harga_jual.append(harga)
    laba_per_unit.append(laba)
    mesin_per_produk.append(mesin)

# Input global kendala mesin dan operator
st.subheader("⚙️ Input Batasan Mesin dan Operator")
operator_per_mesin = st.number_input("Jumlah Operator per Mesin", min_value=1, value=1)
total_operator_tersedia = st.number_input("Total Operator Tersedia", min_value=1, value=10)
total_mesin_tersedia = st.number_input("Total Mesin Tersedia", min_value=1, value=5)

# Format ke rupiah
def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")

# Perhitungan
total_penjualan = [harga_jual[i] * jumlah_produksi[i] for i in range(num_products)]
total_keuntungan = [laba_per_unit[i] * jumlah_produksi[i] for i in range(num_products)]
biaya_unit = [harga_jual[i] - laba_per_unit[i] for i in range(num_products)]
total_biaya = [biaya_unit[i] * jumlah_produksi[i] for i in range(num_products)]

total_all_penjualan = sum(total_penjualan)
total_all_keuntungan = sum(total_keuntungan)
total_all_biaya = sum(total_biaya)

# Perhitungan total mesin & operator
mesin_total_dibutuhkan = sum([jumlah_produksi[i] * mesin_per_produk[i] for i in range(num_products)])
operator_total_dibutuhkan = mesin_total_dibutuhkan * operator_per_mesin

st.subheader("🔎 Kebutuhan Produksi")
st.write(f"🛠️ Total Mesin Dibutuhkan: {mesin_total_dibutuhkan:.2f} dari {total_mesin_tersedia}")
st.write(f"👷 Total Operator Dibutuhkan: {operator_total_dibutuhkan:.2f} dari {total_operator_tersedia}")

# Peringatan jika melebihi batas
if mesin_total_dibutuhkan > total_mesin_tersedia:
    st.error("❌ Mesin yang dibutuhkan melebihi kapasitas.")
if operator_total_dibutuhkan > total_operator_tersedia:
    st.error("❌ Operator yang dibutuhkan melebihi kapasitas.")

# Ringkasan tabel
st.subheader("📊 Ringkasan Perhitungan")
df = pd.DataFrame({
    "Produk": product_names,
    "Jumlah Produksi": jumlah_produksi,
    "Mesin/Unit": mesin_per_produk,
    "Harga Jual/unit": harga_jual,
    "Keuntungan/unit": laba_per_unit,
    "Total Penjualan": total_penjualan,
    "Total Keuntungan": total_keuntungan,
    "Total Biaya Produksi": total_biaya
})
st.dataframe(df.style.format({
    "Total Penjualan": "Rp {:,.0f}",
    "Total Keuntungan": "Rp {:,.0f}",
    "Total Biaya Produksi": "Rp {:,.0f}"
}))

# Total
st.markdown("### 💰 Total Ringkasan")
st.write(f"📦 Total Penjualan: {format_rupiah(total_all_penjualan)}")
st.write(f"💸 Total Biaya Produksi: {format_rupiah(total_all_biaya)}")
st.write(f"✅ Total Keuntungan Bersih: {format_rupiah(total_all_keuntungan)}")

# Grafik
st.subheader("📊 Grafik Perbandingan")
x_pos = np.arange(len(product_names))
width = 0.35
fig, ax = plt.subplots()
bar1 = ax.bar(x_pos - width/2, total_keuntungan, width, label='Keuntungan', color='skyblue')
bar2 = ax.bar(x_pos + width/2, total_penjualan, width, label='Penjualan', color='lightgreen')
max_val = max(total_penjualan + total_keuntungan) if total_penjualan else 0
ax.set_ylim(0, max_val * 1.3)

for bars in [bar1, bar2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                height + 0.03 * max_val,
                f"{int(height):,}".replace(",", "."),
                ha='center', va='bottom', fontsize=10)

ax.set_xticks(x_pos)
ax.set_xticklabels(product_names)
ax.set_ylabel("Rupiah")
ax.set_title("Perbandingan Penjualan dan Keuntungan per Produk")
ax.legend()
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
st.pyplot(fig)

# Saran efisiensi
st.subheader("🧠 Saran Produk Prioritas")
efisiensi = [laba_per_unit[i] / mesin_per_produk[i] if mesin_per_produk[i] > 0 else 0 for i in range(num_products)]
produk_efisien = product_names[np.argmax(efisiensi)]
st.success(f"✅ Produk paling efisien berdasarkan keuntungan/mesin: **{produk_efisien}**")
