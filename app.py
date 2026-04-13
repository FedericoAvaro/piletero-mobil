import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Pileteros Pro", page_icon="💧")

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
    # En tu captura, la pestaña se llama "Personal" y los nombres están en la columna B
    hoja_p = libro.worksheet("Personal")
    # Tomamos la columna 2 (B) saltando el encabezado "Nombre"
    lista_pileteros = [n for n in hoja_p.col_values(2)[1:] if n]
    
    # --- 2. CARGA DE EDIFICIOS ---
    # En tu captura, la pestaña se llama "DB_Edificios" y los nombres en la columna A
    hoja_db = libro.worksheet("DB_Edificios")
    lista_edificios = [e for e in hoja_db.col_values(1)[1:] if e]

    # --- FORMULARIO ---
    user = st.selectbox("¿Quién sos?", lista_pileteros)
    lugar = st.selectbox("Edificio / Consorcio", lista_edificios)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        # Ajustado a 10L según tu columna "Cloro_10L"
        cloro = st.number_input("Cloro (Bidones 10L)", min_value=0.0, step=0.5)
    with c2:
        pastillas = st.number_input("Pastillas (Kg)", min_value=0.0, step=0.5)
        
    gasto = st.number_input("Gasto / Extra ($)", min_value=0, step=100)
    nota = st.text_area("Novedades", placeholder="Ej: Se limpió filtro...")

    if st.button("🚀 GUARDAR REPORTE"):
        if lugar:
            hoja_s = libro.worksheet("Servicios")
            # Armamos la fila según las columnas de tu pestaña "Servicios":
            # Fecha (B), Edificios (C), Tarea (D), Cloro (E), Pastillas (F), Piletero (K), Monto (L)
            # Nota: Usamos append_row. Google Sheets completará las columnas.
            fila = [
                "", # ID (Col A)
                datetime.now().strftime("%d/%m/%Y"), # Fecha (Col B)
                "", # Administradora (Col C) - Podríamos buscarla luego
                lugar, # Edificios (Col D)
                "Visita", # Tarea (Col E)
                cloro, # Cloro (Col F)
                pastillas, # Pastillas (Col G)
                nota, # Extras_Detalles (Col H)
                gasto, # Extras_Montos (Col I)
                "", # Total_Dia (Col J)
                "", # Foto (Col K)
                user # Email_Piletero o Nombre (Col L)
            ]
            hoja_s.append_row(fila)
            st.success("¡Guardado exitosamente!")
            st.balloons()
        else:
            st.warning("Seleccioná un edificio.")

except Exception as e:
    st.error(f"Error de conexión o datos: {e}")
