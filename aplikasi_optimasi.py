import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi", layout="wide")

st.title("1️⃣ Optimasi Produksi (Linear Programming)")
st.markdown("""
### 🔧 Studi Kasus
PT Kreasi Untung Indonesia memproduksi **Meja (X)** dan **Kursi (Y)**. 
Pemilik ingin mengetahui kombinasi produksi terbaik untuk memaksimalkan keuntungan dengan rumus:

\[
Z = c_1 X + c_2 Y
\]
""")

st.markdown("### 📘 Keterangan:")
st.markdown(r"""
- $Z$  = Total keuntungan  
- $c₁$ = Keuntungan per unit Meja  
- $c₂$ = Keuntungan per unit Kursi  
- $X$  = Jumlah Meja  
- $Y$  = Jumlah Kursi
""")

# ===============================
# Input Data
# ===============================
st.markdown("### 💵 Input Harga Jual & Keuntungan per Unit")

col1, col2 = st.columns(2)
with col1:
    x = st.number_input("Jumlah Produksi Meja (X)", min_value=0, value=0)
    laba_meja = st.number_input("Keuntungan per Meja (c₁)", min_value=0, value=0)
    harga_meja = st.number_input("Harga Jual Meja", min_value=0, value=0)
with col2:
    y = st.number_input("Jumlah Produksi Kursi (Y)", min_value=0, value=0)
    laba_kursi = st.number_input("Keuntungan per Kursi (c₂)", min_value=0, value=0)
    harga_kursi = st.number_input("Harga Jual Kursi", min_value=0, value=0)

# Fungsi format rupiah
def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")

# ===============================
# Fungsi Tujuan Z
# ===============================
if all([x, y, laba_meja, laba_kursi]):
    Z = laba_meja * x + laba_kursi * y

    st.subheader("🧮 Perhitungan Fungsi Tujuan")
    st.latex(rf"""
    \begin{{align*}}
    Z &= c_1 \cdot X + c_2 \cdot Y \\
      &= {laba_meja} \cdot {x} + {laba_kursi} \cdot {y} \\
      &= {Z:,.0f}
    \end{{align*}}
    """)

    # ===============================
    # Ringkasan Penjualan & Keuntungan
    # ===============================
    st.markdown("### 💰 Ringkasan Penjualan & Keuntungan")

    total_penjualan_meja = harga_meja * x
    total_penjualan_kursi = harga_kursi * y
    total_penjualan = total_penjualan_meja + total_penjualan_kursi

    biaya_meja = harga_meja - laba_meja
    biaya_kursi = harga_kursi - laba_kursi

    total_biaya = (biaya_meja * x) + (biaya_kursi * y)
    total_laba = laba_meja * x + laba_kursi * y

    st.write(f"🪑 Penjualan Meja: {format_rupiah(total_penjualan_meja)}")
    st.write(f"🪑 Penjualan Kursi: {format_rupiah(total_penjualan_kursi)}")
    st.write(f"📊 Total Penjualan: {format_rupiah(total_penjualan)}")
    st.write(f"💸 Total Keuntungan Bersih: {format_rupiah(total_laba)}")

    # ===============================
    # Grafik Batang
    # ===============================
    st.markdown("### 📊 Grafik Perbandingan")

    kategori = ['Meja (X)', 'Kursi (Y)', 'Total']
    penjualan = [total_penjualan_meja, total_penjualan_kursi, total_penjualan]
    keuntungan = [laba_meja * x, laba_kursi * y, total_laba]

    x_pos = np.arange(len(kategori))
    width = 0.35

    fig, ax = plt.subplots()
    bar1 = ax.bar(x_pos - width/2, keuntungan, width, label='Keuntungan', color='skyblue')
    bar2 = ax.bar(x_pos + width/2, penjualan, width, label='Penjualan', color='lightgreen')

    for bars in [bar1, bar2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.03 * max(penjualan + keuntungan),
                f"{int(height):,}".replace(",", "."),
                ha='center', va='bottom', fontsize=10
            )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(kategori)
    ax.set_title("Perbandingan Penjualan dan Keuntungan")
    ax.set_ylabel("Rupiah")
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))

    st.pyplot(fig)
