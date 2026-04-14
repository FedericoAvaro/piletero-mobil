import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Esto configura el ícono para el acceso directo del celular
st.markdown(
    """
    <head>
        <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/FedericoAvaro/piletero-mobil/main/logo(2).jpg">
        <link rel="icon" href="https://raw.githubusercontent.com/FedericoAvaro/piletero-mobil/main/logo(2).jpg">
    </head>
    """,
    unsafe_allow_html=True
)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pileteros Pro", page_icon="💧")

def conectar_nube():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1WGMYc4dWo8vleTjDtFrYm0FYo9jC32g117c2pnXH2kA")
    except Exception as e:
        st.error(f"Error crítico de conexión: {e}")
        return None

st.title("💧 Registro de Visita")

libro = conectar_nube()

if libro:
    try:
        # 1. CARGA DE DATOS MAESTROS (Personal y Edificios)
        # Traemos personal para mapear Nombre -> Email
        hoja_p = libro.worksheet("Personal")
        datos_p = hoja_p.get_all_records()
        # Creamos un diccionario: {'Sebastian': 'pipipucho@gmail.com', ...}
        dict_pileteros = {p['Nombre '].strip(): p['Email_Piletero'].strip() for p in datos_p if p.get('Nombre ')}
        
        # Traemos edificios desde la base de datos oficial
        hoja_db = libro.worksheet("DB_Edificios")
        lista_edificios = sorted(hoja_db.col_values(1)[1:]) # Columna A sin encabezado

        # --- INTERFAZ DE USUARIO ---
        user_display = st.selectbox("¿Quién sos?", list(dict_pileteros.keys()))
        email_tecnico = dict_pileteros.get(user_display) # Este es el que guardaremos
        
        lugar = st.selectbox("Edificio / Consorcio", lista_edificios)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            cloro = st.number_input("Cloro (Litros)", min_value=0.0, step=0.5, format="%.1f")
        with col2:
            pastillas = st.number_input("Pastillas (Kg)", min_value=0.0, step=0.5, format="%.1f")
            
        st.markdown("### Extras y Gastos")
        gasto_monto = st.number_input("Monto Extra / Gasto ($)", min_value=0, step=100)
        gasto_desc = st.text_input("Motivo del gasto (si aplica)", placeholder="Ej: Compra de acople")
        
        nota = st.text_area("Novedades del servicio", placeholder="Ej: Se reguló el timer de la bomba...")

        # --- LÓGICA DE GUARDADO ---
        if st.button("🚀 GUARDAR REPORTE", use_container_width=True):
            if lugar and user_display:
                with st.spinner("Subiendo datos a la nube..."):
                    hoja_s = libro.worksheet("Servicios")
                    
                    # Generamos una fila que respete EXACTAMENTE tu estructura de Google Sheets
                    # Según tu archivo 'Servicios.csv':
                    # A:ID, B:Fecha, C:Admin, D:Edificios, E:Tarea, F:Cloro, G:Pastillas, ..., L:Email_Piletero
                    
                    fecha_ahora = datetime.now()
                    nueva_fila = ["" for _ in range(21)] # Creamos fila vacía de 21 columnas
                    
                    nueva_fila[0] = fecha_ahora.strftime("%Y%m%d%H%M%S") # ID único
                    nueva_fila[1] = fecha_ahora.strftime("%d/%m/%Y")    # Fecha
                    nueva_fila[3] = lugar                               # Edificios
                    nueva_fila[4] = "Visita"                            # Tarea
                    nueva_fila[5] = cloro                               # Cloro_10L
                    nueva_fila[6] = pastillas                           # Pastillas_KG
                    nueva_fila[11] = email_tecnico                         # Email_Piletero (Columna L)
                    nueva_fila[12] = gasto_monto                        # Gasto_Monto (Columna M)
                    nueva_fila[13] = gasto_desc                         # Gasto_Descripcion
                    nueva_fila[20] = nota                               # Reporte (Columna U)

                    hoja_s.append_row(nueva_fila)
                    
                    st.success(f"¡Excelente {user_display}! Visita en {lugar} registrada.")
                    st.balloons()
            else:
                st.error("Por favor, completa los campos obligatorios.")

    except Exception as e:
        st.error(f"Error al cargar datos del Sheet: {e}")
