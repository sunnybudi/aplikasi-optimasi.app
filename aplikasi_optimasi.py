import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

    st.header("1️⃣ Optimasi Produksi (Linear Programming)")
    st.markdown("""
    ### 🔧 Studi Kasus
    PT Kreasi Untung Indonesia memproduksi **Meja (X)** dan **Kursi (Y)**.
    Model optimasi produksi yang digunakan adalah:
    """)
    st.latex(r"Z = c_1 X + c_2 Y")

    st.markdown("""
    ### 📘 Notasi:
    - $Z$: Total keuntungan
    - $c_1$, $c_2$: Keuntungan per unit Meja/Kursi
    - $X$, $Y$: Jumlah unit Meja/Kursi
    """)

    st.subheader("📥 Input Parameter Produksi")
    col1, col2 = st.columns(2)
    with col1:
        x = st.number_input("Jumlah Produksi Meja (X)", min_value=0, value=0)
        c1 = st.number_input("Keuntungan per Meja (c₁)", min_value=0, value=0)
        waktu_meja = st.number_input("Jam Kerja per Meja", min_value=0.0, value=0.0)
        operator_meja = st.number_input("Operator per Meja", min_value=0.0, value=0.0)
    with col2:
        y = st.number_input("Jumlah Produksi Kursi (Y)", min_value=0, value=0)
        c2 = st.number_input("Keuntungan per Kursi (c₂)", min_value=0, value=0)
        waktu_kursi = st.number_input("Jam Kerja per Kursi", min_value=0.0, value=0.0)
        operator_kursi = st.number_input("Operator per Kursi", min_value=0.0, value=0.0)

    st.subheader("🛠️ Batasan Sumber Daya")
    col3, col4 = st.columns(2)
    with col3:
        max_waktu = st.number_input("Total Jam Kerja Tersedia", value=0.0, min_value=0.0)
    with col4:
        max_operator = st.number_input("Total Operator Tersedia", value=0.0, min_value=0.0)

    if all([x, y, c1, c2, waktu_meja, waktu_kursi, operator_meja, operator_kursi, max_waktu, max_operator]):
        total_keuntungan = c1 * x + c2 * y
        waktu_dipakai = waktu_meja * x + waktu_kursi * y
        operator_dipakai = operator_meja * x + operator_kursi * y

        st.subheader("🧮 Perhitungan Fungsi Tujuan")
        st.latex(rf"""
        \begin{{align*}}
        Z &= c_1 X + c_2 Y \\
          &= {c1} \cdot {x} + {c2} \cdot {y} \\
          &= {total_keuntungan:,.0f}
        \end{{align*}}
        """)

        st.markdown("### ✅ Evaluasi Kendala")
        st.write(f"⏱️ Total Jam Kerja Digunakan: **{waktu_dipakai}** dari maksimum {max_waktu}")
        st.write(f"👷 Total Operator Digunakan: **{operator_dipakai}** dari maksimum {max_operator}")

        waktu_ok = waktu_dipakai <= max_waktu
        operator_ok = operator_dipakai <= max_operator

        if waktu_ok and operator_ok:
            st.success("✅ Produksi memenuhi semua kendala sumber daya!")
        else:
            if not waktu_ok:
                st.error("❌ Produksi melebihi batas jam kerja!")
            if not operator_ok:
                st.error("❌ Produksi melebihi batas jumlah operator!")

        # Grafik perbandingan
        st.markdown("### 📊 Grafik Perbandingan Produksi & Keuntungan")
        kategori = ['Meja (X)', 'Kursi (Y)']
        produksi = [x, y]
        keuntungan = [c1 * x, c2 * y]

        x_pos = np.arange(len(kategori))
        width = 0.35
        fig, ax = plt.subplots(figsize=(8, 4))
        bar1 = ax.bar(x_pos - width/2, keuntungan, width=width, label='Keuntungan', color='skyblue')
        bar2 = ax.bar(x_pos + width/2, produksi, width=width, label='Jumlah Produksi', color='lightgreen')

        max_val = max(keuntungan + produksi) * 1.2
        ax.set_ylim(0, max_val)

        for bars in [bar1, bar2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.0f}", ha='center', fontsize=9)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(kategori)
        ax.set_ylabel("Nilai")
        ax.set_title("Produksi & Keuntungan per Produk")
        ax.legend()
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))

        st.pyplot(fig)
