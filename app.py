import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. SIEMPRE PRIMERO: Configuración de la página
st.set_page_config(page_title="Pileteros Pro", page_icon="💧")

# 2. SEGUNDO: El ícono para el celular (Sin la 'f' delante y con links limpios)
st.markdown(
    """
    <head>
        <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/FedericoAvaro/piletero-mobil/main/logo.jpg">
        <link rel="icon" href="https://raw.githubusercontent.com/FedericoAvaro/piletero-mobil/main/logo.jpg" type="image/jpeg">
    </head>
    """,
    unsafe_allow_html=True
)

def conectar_nube():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
    
    client = gspread.authorize(creds)
    return client.open_by_key("1WGMYc4dWo8vleTjDtFrYm0FYo9jC32g117c2pnXH2kA")

st.title("💧 Registro de Visita")

try:
    libro = conectar_nube()
    
    # --- 1. CARGA DE PILETEROS ---
    hoja_p = libro.worksheet("Personal")
    lista_pileteros = [n for n in hoja_p.col_values(2)[1:] if n]
    
    # --- 2. CARGA DE EDIFICIOS ---
    hoja_db = libro.worksheet("DB_Edificios")
    lista_edificios = [e for e in hoja_db.col_values(1)[1:] if e]

    # --- FORMULARIO ---
    user = st.selectbox("¿Quién sos?", lista_pileteros)
    lugar = st.selectbox("Edificio / Consorcio", lista_edificios)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        cloro = st.number_input("Cloro (Bidones 10L)", min_value=0.0, step=0.5)
    with c2:
        pastillas = st.number_input("Pastillas (Kg)", min_value=0.0, step=0.5)
        
    gasto = st.number_input("Gasto / Extra ($)", min_value=0, step=100)
    nota = st.text_area("Novedades", placeholder="Ej: Se limpió filtro...")

    if st.button("🚀 GUARDAR REPORTE"):
        if lugar:
            try:
                hoja_s = libro.worksheet("Servicios")
                nuevo_id = datetime.now().strftime("%Y%m%d%H%M%S")

                nueva_fila = [
                    nuevo_id,
                    datetime.now().strftime("%d/%m/%Y"),
                    "",
                    lugar,
                    "Visita",
                    cloro,
                    pastillas,
                    nota,
                    gasto,
                    "",
                    "",
                    user
                ]
                
                hoja_s.append_row(nueva_fila, table_range="A1")
                st.success(f"✅ Reporte de '{lugar}' enviado correctamente.")
                st.balloons()
                
            except Exception as e_save:
                st.error(f"Hubo un problema al guardar: {e_save}")
        else:
            st.warning("Por favor, seleccioná un edificio primero.")

except Exception as e:
    st.error(f"Error de conexión o datos: {e}")
