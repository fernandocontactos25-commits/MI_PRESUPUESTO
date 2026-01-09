import streamlit as st
import pandas as pd
import json
import os

# Configuración de la página para móviles
st.set_page_config(page_title="Mi Gestor Pro", layout="centered")

# --- PERSISTENCIA DE DATOS ---
def cargar_datos():
    if os.path.exists("db_movil.json"):
        with open("db_movil.json", "r") as f: return json.load(f)
    return {"plantilla_fijos": [], "historial": {}}

def guardar_datos(datos):
    with open("db_movil.json", "w") as f: json.dump(datos, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = cargar_datos()

# --- INTERFAZ ---
st.title("📊 Gestor Financiero")

# 1. Selección de Mes
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_sel = st.selectbox("Selecciona el Mes:", meses)

# Inicializar mes en historial si no existe
if mes_sel not in st.session_state.db["historial"]:
    st.session_state.db["historial"][mes_sel] = {"ingreso": 0.0, "variables": []}

# 2. Ingreso del Mes
ingreso = st.number_input("Ingreso del Mes S/.", 
                         value=float(st.session_state.db["historial"][mes_sel]["ingreso"]),
                         step=100.0)
st.session_state.db["historial"][mes_sel]["ingreso"] = ingreso

# 3. Gastos Fijos (Plantilla)
with st.expander("⚙️ Configurar Plantilla Gastos Fijos"):
    f_nom = st.text_input("Nombre Gasto Fijo")
    f_mon = st.number_input("Monto Fijo S/.", min_value=0.0)
    if st.button("Añadir a Plantilla"):
        st.session_state.db["plantilla_fijos"].append({"nombre": f_nom, "monto": f_mon})
        guardar_datos(st.session_state.db)
        st.rerun()

# 4. Registrar Gasto Variable
st.subheader("💸 Nuevo Gasto Variable")
v_nom = st.text_input("Descripción (Ej: Cena, Taxi)")
v_mon = st.number_input("Monto S/.", key="var_mon", min_value=0.0)
if st.button("Registrar Gasto"):
    st.session_state.db["historial"][mes_sel]["variables"].append({"desc": v_nom, "monto": v_mon})
    guardar_datos(st.session_state.db)
    st.success("Registrado")
    st.rerun()

# --- RESUMEN Y GRÁFICO ---
st.divider()
total_fijos = sum(f["monto"] for f in st.session_state.db["plantilla_fijos"])
total_vars = sum(v["monto"] for v in st.session_state.db["historial"][mes_sel]["variables"])
saldo = ingreso - total_fijos - total_vars

col1, col2 = st.columns(2)
col1.metric("Total Gastos", f"S/. {total_fijos + total_vars:.2f}")
col2.metric("Saldo Neto", f"S/. {saldo:.2f}", delta=saldo)

# Gráfico Comparativo de Meses
st.subheader("📈 Evolución de Meses")
data_grafico = []
for m in meses:
    if m in st.session_state.db["historial"]:
        d = st.session_state.db["historial"][m]
        g_v = sum(v["monto"] for v in d["variables"])
        data_grafico.append({
            "Mes": m,
            "Ingresos": d["ingreso"],
            "Gastos": total_fijos + g_v
        })

if data_grafico:
    df = pd.DataFrame(data_grafico)
    st.bar_chart(df.set_index("Mes"))

# Botón para borrar datos
if st.button("Limpiar Todo"):
    if st.checkbox("Confirmar borrado completo"):
        st.session_state.db = {"plantilla_fijos": [], "historial": {}}
        guardar_datos(st.session_state.db)
        st.rerun()