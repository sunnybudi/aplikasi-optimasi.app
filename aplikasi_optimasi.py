import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

st.set_page_config(page_title="Optimasi Produksi - Mesin & Operator", layout="wide")
st.title("🔧 Optimasi Produksi - Jumlah Mesin & Operator Produksi")

# ---------- Penjelasan Rumus ----------
st.subheader(r"""
📘 Rumus Optimasi Produksi

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

st.markdown(r"""
## 📈 Rumus Optimasi Produksi (Linear Programming)
Misalkan:
- \( X_1, X_2, \dots, X_n \): jumlah unit masing-masing produk
- \( c_1, c_2, \dots, c_n \): keuntungan per unit masing-masing produk
- \( o_1, o_2, \dots, o_n \): operator per unit produk (mesin × operator per mesin)
- \( m_1, m_2, \dots, m_n \): mesin per unit produk
- \( O \): total operator tersedia
- \( M \): total mesin tersedia

### Fungsi Objektif:
$$
\text{Maksimalkan } Z = c_1X_1 + c_2X_2 + \dots + c_nX_n
$$

### Kendala:
$$
o_1X_1 + o_2X_2 + \dots + o_nX_n \leq O \\
m_1X_1 + m_2X_2 + \dots + m_nX_n \leq M \\
X_1, X_2, \dots, X_n \geq 0
$$
""")

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

    st.header("⚙️ Input untuk Optimasi")
    total_operator_avail = st.number_input("Total Operator Tersedia", min_value=1, value=100)
    total_mesin_avail = st.number_input("Total Mesin Tersedia", min_value=1, value=50)

# ---------- Fungsi Tambahan ----------
def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")

# ---------- Perhitungan ----------
total_penjualan = [harga_jual[i] * jumlah_produksi[i] for i in range(num_products)]
total_keuntungan = [laba_per_unit[i] * jumlah_produksi[i] for i in range(num_products)]
biaya_unit = [harga_jual[i] - laba_per_unit[i] for i in range(num_products)]
total_biaya = [biaya_unit[i] * jumlah_produksi[i] for i in range(num_products)]
total_operator_per_produk = [mesin_digunakan[i] * operator_per_mesin[i] for i in range(num_products)]
efisiensi_per_produk = [
    total_keuntungan[i] / total_operator_per_produk[i] if total_operator_per_produk[i] > 0 else 0
    for i in range(num_products)
]

# ---------- Optimasi Produksi Otomatis ----------
st.subheader("📌 Hasil Optimasi Produksi Maksimum")
model = LpProblem("Optimasi_Produksi", LpMaximize)
X = [LpVariable(f"X{i+1}", lowBound=0, cat='Integer') for i in range(num_products)]
model += lpSum([laba_per_unit[i] * X[i] for i in range(num_products)])
model += lpSum([mesin_digunakan[i] * operator_per_mesin[i] * X[i] for i in range(num_products)]) <= total_operator_avail
model += lpSum([mesin_digunakan[i] * X[i] for i in range(num_products)]) <= total_mesin_avail
model.solve()

for i, var in enumerate(X):
    st.write(f"🔹 {product_names[i]} ➜ Jumlah Optimal: **{int(var.value())} unit**")

st.success(f"🎯 Total Keuntungan Maksimum: **{format_rupiah(int(model.objective.value()))}**")

# ---------- Ringkasan dan Visualisasi ----------
total_all_penjualan = sum(total_penjualan)
total_all_keuntungan = sum(total_keuntungan)
total_all_biaya = sum(total_biaya)
total_mesin = sum(mesin_digunakan)
total_operator = sum(total_operator_per_produk)
total_all_produksi = sum(jumlah_produksi)

# ---------- Dataframe Utama ----------
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

# Format tampilan
st.subheader("📊 Ringkasan Produksi")
df_clean = df.copy()
for col in df_clean.columns:
    if col in ["Total Penjualan", "Total Keuntungan", "Total Biaya Produksi"]:
        df_clean[col] = df_clean[col].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
    elif col in ["Harga Jual/unit", "Keuntungan/unit"]:
        df_clean[col] = df_clean[col].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") + " /unit")
    elif col == "Efisiensi (Rp/Operator)":
        df_clean[col] = df_clean[col].apply(lambda x: f"Rp {int(x):,}".replace(",", ".") + " /orang")
    elif col == "Jumlah Produksi":
        df_clean[col] = df_clean[col].apply(lambda x: f"{int(x)} unit")
    elif col == "Mesin Digunakan":
        df_clean[col] = df_clean[col].apply(lambda x: f"{int(x)} unit")
    elif col == "Total Operator":
        df_clean[col] = df_clean[col].apply(lambda x: f"{int(x)} orang")
    elif col == "Operator/Mesin":
        df_clean[col] = df_clean[col].apply(lambda x: f"{int(x)} orang")

st.dataframe(df_clean.set_index("Produk").T)

# Ringkasan Total
st.subheader("🧾 Ringkasan Total Produksi")
df_total = pd.DataFrame({
    "Keterangan": [
        "Total Produksi",
        "Total Penjualan",
        "Total Biaya Produksi",
        "Total Keuntungan Bersih",
        "Total Mesin Digunakan",
        "Total Operator Dibutuhkan"
    ],
    "Nilai": [
        f"{int(total_all_produksi)} unit",
        format_rupiah(total_all_penjualan),
        format_rupiah(total_all_biaya),
        format_rupiah(total_all_keuntungan),
        f"{int(total_mesin)} unit",
        f"{int(total_operator)} orang"
    ]
})

st.dataframe(df_total)

# Prioritas Efisien
st.subheader("📌 Rekomendasi Prioritas Produksi")
df_prioritas = pd.DataFrame({
    "Produk": product_names,
    "Efisiensi": efisiensi_per_produk,
    "Total Keuntungan": total_keuntungan
}).sort_values(by="Efisiensi", ascending=False).reset_index(drop=True)

produk_efisien = df_prioritas.iloc[0]["Produk"]
efisiensi_tertinggi = df_prioritas.iloc[0]["Efisiensi"]
st.success(f"✅ Produk yang paling efisien diproduksi: **{produk_efisien}** (Efisiensi: {format_rupiah(efisiensi_tertinggi)} per operator)")

# Grafik Perbandingan
st.subheader("📊 Diagram Perbandingan")
x_pos = np.arange(len(product_names) + 1)
width = 0.35
fig, ax = plt.subplots()
all_product_names = product_names + ["Total Semua Produk"]
total_penjualan_all = total_penjualan + [total_all_penjualan]
total_keuntungan_all = total_keuntungan + [total_all_keuntungan]

bar1 = ax.bar(x_pos - width/2, total_keuntungan_all, width, label='Keuntungan', color='skyblue')
bar2 = ax.bar(x_pos + width/2, total_penjualan_all, width, label='Penjualan', color='lightgreen')

max_val = max(total_penjualan_all + total_keuntungan_all)
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
