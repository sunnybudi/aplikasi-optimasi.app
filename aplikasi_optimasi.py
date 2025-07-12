import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus

st.set_page_config(page_title="Optimasi Produksi - Mesin & Operator", layout="wide")
st.title("🔧 Aplikasi Produksi - Mesin & Operator")

# Tabs
tab1, tab2 = st.tabs(["📈 Optimasi Produksi", "📊 Perhitungan Produksi"])

# ---------- Input: SEMUA di SIDEBAR ----------
with st.sidebar:
    st.header("📦 Input Jumlah Produk")
    num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

    st.header("📥 Input Data Produk")

    product_names = []
    jumlah_produksi = []
    harga_jual = []
    laba_per_unit = []
    mesin_digunakan = []
    operator_per_mesin = []

    for i in range(num_products):
        st.markdown(f"### 🔹 Produk {i+1}")
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
        qty = st.number_input(f"Jumlah Produksi Produk {i+1}", min_value=0, value=0, key=f"qty_{i}")
        harga = st.number_input(f"Harga Jual/unit Produk {i+1}", min_value=0, value=0, key=f"harga_{i}")
        laba = st.number_input(f"Keuntungan/unit Produk {i+1}", min_value=0, value=0, key=f"laba_{i}")
        mesin = st.number_input(f"Jumlah Mesin Produk {i+1}", min_value=0, value=0, key=f"mesin_{i}")
        op_mesin = st.number_input(f"Operator per Mesin Produk {i+1}", min_value=1, value=1, key=f"opmesin_{i}")

        product_names.append(name)
        jumlah_produksi.append(qty)
        harga_jual.append(harga)
        laba_per_unit.append(laba)
        mesin_digunakan.append(mesin)
        operator_per_mesin.append(op_mesin)

# ---------- Perhitungan ----------
def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")

total_penjualan = [harga_jual[i] * jumlah_produksi[i] for i in range(num_products)]
total_keuntungan = [laba_per_unit[i] * jumlah_produksi[i] for i in range(num_products)]
biaya_unit = [harga_jual[i] - laba_per_unit[i] for i in range(num_products)]
total_biaya = [biaya_unit[i] * jumlah_produksi[i] for i in range(num_products)]
total_operator_per_produk = [mesin_digunakan[i] * operator_per_mesin[i] for i in range(num_products)]
efisiensi_per_produk = [
    total_keuntungan[i] / total_operator_per_produk[i] if total_operator_per_produk[i] > 0 else 0
    for i in range(num_products)
]

total_all_penjualan = sum(total_penjualan)
total_all_keuntungan = sum(total_keuntungan)
total_all_biaya = sum(total_biaya)
total_mesin = sum(mesin_digunakan)
total_operator = sum(total_operator_per_produk)
total_all_produksi = sum(jumlah_produksi)

# ---------- Tab 1: Optimasi Produksi ----------
with tab1:
    st.subheader("📈 Optimasi Produksi Berdasarkan Keuntungan Maksimum")
    st.markdown(r"""
    $$
    \begin{aligned}
    \text{Maksimalkan } &Z = c_1X_1 + c_2X_2 + \cdots + c_nX_n \\
    \text{dengan kendala:} \\
    &a_{11}X_1 + a_{12}X_2 + \cdots + a_{1n}X_n \leq b_1 \quad \text{(kendala operator)} \\
    &a_{21}X_1 + a_{22}X_2 + \cdots + a_{2n}X_n \leq b_2 \quad \text{(kendala mesin)} \\
    &X_1, X_2, \dots, X_n \geq 0
    \end{aligned}
    $$
    """)
    st.markdown("""
    **Keterangan:**

    - \( Z \): Total keuntungan yang ingin dimaksimalkan  
    - \( c_i \): Keuntungan per unit produk ke-\( i \)  
    - \( X_i \): Jumlah unit produk ke-\( i \) yang diproduksi  
    - \( a_{1i} \): Jumlah operator per unit produk ke-\( i \)  
    - \( b_1 \): Total operator yang tersedia  
    - \( a_{2i} \): Jumlah mesin per unit produk ke-\( i \)  
    - \( b_2 \): Total mesin yang tersedia
    """)

    total_operator_tersedia = st.number_input("Masukkan Total Operator yang Tersedia", min_value=1, value=10)
    total_mesin_tersedia = st.number_input("Masukkan Total Mesin yang Tersedia", min_value=1, value=5)

    if all(laba > 0 for laba in laba_per_unit) and total_operator_tersedia > 0 and total_mesin_tersedia > 0:
        x = [LpVariable(f"x{i+1}", lowBound=0, cat='Integer') for i in range(num_products)]
        model = LpProblem("Optimasi_Produksi", LpMaximize)
        model += lpSum([laba_per_unit[i] * x[i] for i in range(num_products)]), "Total_Keuntungan"
        model += lpSum([mesin_digunakan[i] * operator_per_mesin[i] * x[i] for i in range(num_products)]) <= total_operator_tersedia, "Batas_Operator"
        model += lpSum([mesin_digunakan[i] * x[i] for i in range(num_products)]) <= total_mesin_tersedia, "Batas_Mesin"

        model.solve()

        if LpStatus[model.status] == "Optimal":
            st.success("✅ Solusi optimal ditemukan:")
            for i in range(num_products):
                jumlah_unit = int(x[i].value())
                mesin_total = mesin_digunakan[i] * jumlah_unit
                operator_total = mesin_total * operator_per_mesin[i]

                st.write(f"🔹 {product_names[i]} ➜ Jumlah Optimal: **{jumlah_unit} unit**")
                st.caption(f"Perhitungan: Mesin = {mesin_digunakan[i]} × {jumlah_unit} = {mesin_total}, Operator = {mesin_total} × {operator_per_mesin[i]} = {operator_total}")

            st.write(f"💰 Total Keuntungan Maksimal: **{format_rupiah(model.objective.value())}**")
        else:
            st.error("❌ Tidak ada solusi optimal ditemukan. Periksa kembali input dan batasan operator/mesin.")
    else:
        st.info("ℹ️ Masukkan data produk, total operator dan mesin yang tersedia untuk melihat hasil optimasi.")

# ---------- Tab 2: Perhitungan Produksi ----------
with tab2:
    st.subheader("📘 Rumus Perhitungan Produksi")
    st.markdown(r"""
    $$
    \begin{array}{ll}
    \text{Total Penjualan} &= \text{Harga Jual per Unit} \times \text{Jumlah Produksi} \\
    \text{Total Keuntungan} &= \text{Laba per Unit} \times \text{Jumlah Produksi} \\
    \text{Total Biaya Produksi} &= (\text{Harga Jual per Unit} - \text{Laba per Unit}) \times \text{Jumlah Produksi} \\
    \text{Total Operator} &= \text{Jumlah Mesin} \times \text{Operator per Mesin} \\
    \text{Efisiensi} &= \dfrac{\text{Total Keuntungan}}{\text{Total Operator}}
    \end{array}
    $$
    """)
    
    st.subheader("📊 Perhitungan Produksi")
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

    for col in df.columns:
        if col in ["Total Penjualan", "Total Keuntungan", "Total Biaya Produksi"]:
            df[col] = df[col].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
        elif col in ["Harga Jual/unit", "Keuntungan/unit"]:
            df[col] = df[col].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") + " /unit")
        elif col == "Efisiensi (Rp/Operator)":
            df[col] = df[col].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") + " /orang")
        elif col in ["Jumlah Produksi", "Mesin Digunakan"]:
            df[col] = df[col].apply(lambda x: f"{int(x)} unit")
        elif col == "Total Operator":
            df[col] = df[col].apply(lambda x: f"{int(x)} orang")
        elif col == "Operator/Mesin":
            df[col] = df[col].apply(lambda x: f"{int(x)} orang")

    st.dataframe(df.set_index("Produk").T.style.set_properties(**{'text-align': 'left'}))

    total_summary = {
        "Total Produksi": f"{int(total_all_produksi)} unit",
        "Total Penjualan": format_rupiah(total_all_penjualan),
        "Total Biaya Produksi": format_rupiah(total_all_biaya),
        "Total Keuntungan Bersih": format_rupiah(total_all_keuntungan),
        "Total Mesin Digunakan": f"{int(total_mesin)} unit",
        "Total Operator Dibutuhkan": f"{int(total_operator)} orang"
    }
    df_total = pd.DataFrame(list(total_summary.items()), columns=["Keterangan", "Nilai"])
    st.subheader("🧾 Ringkasan Total Produksi")
    st.dataframe(df_total)

    df_prioritas = pd.DataFrame({
        "Produk": product_names,
        "Efisiensi": efisiensi_per_produk,
        "Total Keuntungan": total_keuntungan
    }).sort_values(by="Efisiensi", ascending=False).reset_index(drop=True)
    produk_efisien = df_prioritas.iloc[0]["Produk"]
    efisiensi_tertinggi = df_prioritas.iloc[0]["Efisiensi"]
    st.success(f"✅ Produk yang paling efisien diproduksi: **{produk_efisien}** (Efisiensi: {format_rupiah(efisiensi_tertinggi)} per operator)")

    st.subheader("📊 Diagram Perbandingan")
    x_pos = np.arange(len(product_names) + 1)
    width = 0.35
    fig, ax = plt.subplots()
    all_product_names = product_names + ["Total Semua Produk"]
    total_penjualan_all = total_penjualan + [total_all_penjualan]
    total_keuntungan_all = total_keuntungan + [total_all_keuntungan]

    bar1 = ax.bar(x_pos - width/2, total_keuntungan_all, width, label='Keuntungan', color='skyblue')
    bar2 = ax.bar(x_pos + width/2, total_penjualan_all, width, label='Penjualan', color='lightgreen')

    max_val = max([int(val) for val in total_penjualan_all + total_keuntungan_all])
    ax.set_ylim(0, max_val * 1.3)
    for bars in [bar1, bar2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2,
                    height + 0.01 * max_val,
                    f"{int(height):,}".replace(",", "."),
                    ha='center', va='bottom', fontsize=9)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(all_product_names, rotation=0, fontsize=9)
    ax.set_ylabel("Nilai (Rupiah)", fontsize=10)
    ax.set_title("Perbandingan Penjualan dan Keuntungan per Produk", fontsize=11)
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
    fig.tight_layout()
    st.pyplot(fig)
