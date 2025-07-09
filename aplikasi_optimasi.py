import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.optimize import linprog

st.set_page_config(page_title="Optimasi Produksi", layout="wide")

tab1, tab2 = st.tabs(["🔧 Optimasi Produksi", "📊 Visualisasi"])

with tab1:
    st.header("1️⃣ Optimasi Produksi (Linear Programming)")
    st.markdown("""
    ### 🔧 Studi Kasus
    PT Kreasi Untung Indonesia memproduksi **Meja (X)** dan **Kursi (Y)**.
    Fungsi keuntungan:
    """)
    st.latex(r"Z = c₁X + c₂Y")

    st.markdown("### 📘 Keterangan:")
    st.markdown(r"""
    - $Z$: Total keuntungan  
    - $c₁$: Keuntungan per unit Meja  
    - $c₂$: Keuntungan per unit Kursi  
    - $X$: Jumlah Meja  
    - $Y$: Jumlah Kursi
    """)

    col1, col2 = st.columns(2)
    with col1:
        x = st.number_input("Jumlah Produksi Meja (X)", value=0.0)
        laba_meja = st.number_input("Keuntungan per Meja (c₁)", value=0.0)
        harga_meja = st.number_input("Harga Jual Meja", value=0.0)
    with col2:
        y = st.number_input("Jumlah Produksi Kursi (Y)", value=0.0)
        laba_kursi = st.number_input("Keuntungan per Kursi (c₂)", value=0.0)
        harga_kursi = st.number_input("Harga Jual Kursi", value=0.0)

    def format_rupiah(nilai):
        return f"Rp {nilai:,.0f}".replace(",", ".")

    if all([laba_meja, laba_kursi, x, y]):
        Z = laba_meja * x + laba_kursi * y
        st.subheader("🧮 Perhitungan Fungsi Tujuan Z")
        st.latex(rf"""
        \begin{{align*}}
        Z &= c_1 \cdot X + c_2 \cdot Y \\
          &= {laba_meja} \cdot {x} + {laba_kursi} \cdot {y} \\
          &= {Z:,.0f}
        \end{{align*}}
        """)

    total_penjualan = harga_meja * x + harga_kursi * y
    total_keuntungan = laba_meja * x + laba_kursi * y

    st.markdown("### 💰 Ringkasan Total Penjualan & Keuntungan")
    st.write(f"Penjualan Meja: {format_rupiah(harga_meja * x)}")
    st.write(f"Penjualan Kursi: {format_rupiah(harga_kursi * y)}")
    st.write(f"Total Penjualan: {format_rupiah(total_penjualan)}")
    st.write(f"Total Keuntungan Bersih: {format_rupiah(total_keuntungan)}")

    st.markdown("### 📊 Diagram Perbandingan")
    kategori = ["Meja", "Kursi", "Total"]
    penjualan = [harga_meja * x, harga_kursi * y, total_penjualan]
    keuntungan = [laba_meja * x, laba_kursi * y, total_keuntungan]
    x_pos = np.arange(len(kategori))
    width = 0.35

    fig1, ax1 = plt.subplots()
    bar1 = ax1.bar(x_pos - width/2, keuntungan, width, label="Keuntungan", color='skyblue')
    bar2 = ax1.bar(x_pos + width/2, penjualan, width, label="Penjualan", color='lightgreen')

    for bars in [bar1, bar2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + 5, f"{height:,.0f}", ha='center', fontsize=9)

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(kategori)
    ax1.set_title("Perbandingan Penjualan dan Keuntungan")
    ax1.set_ylabel("Rupiah")
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
    ax1.legend()
    st.pyplot(fig1)

    # ============================================
    # 🔧 Tambahan: OPTIMASI PRODUKSI TENAGA KERJA
    # ============================================
    st.markdown("### 👷‍♂️ Optimasi Berdasarkan Kendala Tenaga Kerja")

    col_op1, col_op2 = st.columns(2)
    with col_op1:
        tenaga_meja = st.number_input("Tenaga Kerja per Meja", value=0.0)
    with col_op2:
        tenaga_kursi = st.number_input("Tenaga Kerja per Kursi", value=0.0)

    total_operator = st.number_input("Total Tenaga Kerja Tersedia", value=0.0)

    if all([tenaga_meja, tenaga_kursi, laba_meja, laba_kursi, total_operator]):
        c = [-laba_meja, -laba_kursi]
        A = [[tenaga_meja, tenaga_kursi]]
        b = [total_operator]
        bounds = [(0, None), (0, None)]

        result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

        if result.success:
            x_opt, y_opt = result.x
            keuntungan_opt = -result.fun

            st.success("✅ Hasil Optimasi:")
            st.write(f"Jumlah Meja: {x_opt:.2f}")
            st.write(f"Jumlah Kursi: {y_opt:.2f}")
            st.write(f"Total Keuntungan Maksimum: {format_rupiah(keuntungan_opt)}")

            fig2, ax2 = plt.subplots()
            produk = ['Meja', 'Kursi']
            jumlah = [x_opt, y_opt]
            profit = [x_opt * laba_meja, y_opt * laba_kursi]

            barx = np.arange(len(produk))
            bar1 = ax2.bar(barx - 0.2, jumlah, 0.4, label='Produksi')
            bar2 = ax2.bar(barx + 0.2, profit, 0.4, label='Keuntungan')

            for bars in [bar1, bar2]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.1f}", ha='center', fontsize=9)

            ax2.set_xticks(barx)
            ax2.set_xticklabels(produk)
            ax2.set_ylabel("Jumlah / Rupiah")
            ax2.set_title("Optimasi Produksi Berdasarkan Tenaga Kerja")
            ax2.legend()
            st.pyplot(fig2)
        else:
            st.error("❌ Optimasi gagal. Periksa input data.")
