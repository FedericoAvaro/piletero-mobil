import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# Configuración de página
st.set_page_config(page_title="Pileteros Pro", page_icon="💧")

# Función para conectar usando Secrets (Seguro) o Local (JSON)
def conectar_nube():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 1. Verificamos si estamos en la nube (Secrets)
    if "gcp_service_account" in st.secrets:
        # IMPORTANTE: Aquí NO usamos json.loads. 
        # Convertimos el secreto directamente a diccionario.
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # 2. Si estamos en local (Tu PC), usamos el archivo físico
        creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
    
    client = gspread.authorize(creds)
    return client.open_by_key("1WGMYc4dWo8vleTjDtFrYm0FYo9jC32g117c2pnXH2kA")
st.title("💧 Registro de Visita")

try:
    libro = conectar_nube()
    
    # Traemos los nombres del Personal para el selector
    hoja_p = libro.worksheet("Personal")
    lista_pileteros = [p['Nombre'] for p in hoja_p.get_all_records() if p.get('Nombre')]
    
    # Traemos los edificios para el selector
    # Asumo que tenés una lista de edificios en alguna solapa o la extraemos de Servicios
    hoja_s = libro.worksheet("Servicios")
    columna_edificios = hoja_s.col_values(2) # Ajustar según columna real
    lista_edificios = sorted(list(set(columna_edificios[1:]))) 

    # --- FORMULARIO ---
    user = st.selectbox("¿Quién sos?", lista_pileteros)
    lugar = st.selectbox("Edificio / Consorcio", lista_edificios)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        cloro = st.number_input("Cloro (L)", min_value=0.0, step=0.5)
    with c2:
        pastillas = st.number_input("Pastillas (Kg)", min_value=0.0, step=0.5)
        
    gasto = st.number_input("Gasto / Extra ($)", min_value=0, step=100)
    nota = st.text_area("Novedades", placeholder="Ej: Se limpió filtro...")

    if st.button("🚀 GUARDAR REPORTE"):
        if lugar:
            # Orden de columnas: Fecha, Edificio, Cloro, Past, Piletero, Monto_Extra, Tarea_Realizada
            fila = [
                datetime.now().strftime("%d/%m/%Y"),
                lugar,
                cloro,
                pastillas,
                user,
                gasto,
                nota
            ]
            hoja_s.append_row(fila)
            st.success("¡Guardado! Ya podés cerrar.")
            st.balloons()
        else:
            st.warning("Seleccioná un edificio.")

except Exception as e:
    st.error(f"Error de conexión: {e}")