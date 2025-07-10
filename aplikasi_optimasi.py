import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("⚙️ Optimasi Produksi dengan Kendala Sumber Daya")

# Sidebar - Input Jumlah Produk
st.sidebar.header("📦 Jumlah Produk")
num_products = st.sidebar.number_input("Jumlah Produk", min_value=1, value=2, step=1)

# Sidebar - Input Data Produk
st.sidebar.header("📥 Input Data Produk")

product_names = []
profits = []
resource_per_unit = []
mesin_per_produk = []
operator_per_mesin = []

for i in range(num_products):
    st.sidebar.subheader(f"🔹 Produk {i+1}")
    name = st.sidebar.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    profit = st.sidebar.number_input(f"Keuntungan/unit", value=10.0, step=1.0, key=f"profit_{i}")
    usage = st.sidebar.number_input(f"Sumber Daya/unit", value=1.0, step=1.0, key=f"usage_{i}")
    mesin = st.sidebar.number_input(f"Jumlah Mesin", min_value=1, value=1, key=f"mesin_{i}")
    op_mesin = st.sidebar.number_input(f"Operator/Mesin", min_value=1, value=1, key=f"opmesin_{i}")

    product_names.append(name)
    profits.append(profit)
    resource_per_unit.append(usage)
    mesin_per_produk.append(mesin)
    operator_per_mesin.append(op_mesin)

# Sidebar - Total sumber daya
st.sidebar.header("⚙️ Total Sumber Daya")
total_resource = st.sidebar.number_input("Total Sumber Daya Tersedia", value=100.0, step=1.0)

# -------------------------------
# Optimasi Produksi
# -------------------------------
c = [-p for p in profits]  # Maksimalkan keuntungan = minimalkan negatif
A = [resource_per_unit]
b = [total_resource]
bounds = [(0, None)] * num_products

result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

# -------------------------------
# Hasil Optimasi
# -------------------------------
st.subheader("📊 Hasil Optimasi Produksi")

if result.success:
    optimal_qty = np.round(result.x, 2)
    total_profit = -result.fun
    total_keuntungan = optimal_qty * profits
    total_operator = [mesin_per_produk[i] * operator_per_mesin[i] for i in range(num_products)]

    df_result = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Optimal": optimal_qty,
        "Keuntungan/unit": profits,
        "Total Keuntungan": np.round(total_keuntungan, 2),
        "Mesin": mesin_per_produk,
        "Operator/Mesin": operator_per_mesin,
        "Total Operator": total_operator
    })

    st.dataframe(df_result.style.format({
        "Keuntungan/unit": "Rp {:,.0f}",
        "Total Keuntungan": "Rp {:,.0f}"
    }))

    st.success(f"💰 Total Keuntungan Maksimum: **Rp {total_profit:,.0f}**".replace(",", "."))
    st.info(f"👷 Total Operator Dibutuhkan (berdasarkan jumlah mesin): **{int(sum(total_operator))} orang**")
else:
    st.error("❌ Optimasi gagal. Periksa input sumber daya dan parameter lainnya.")
