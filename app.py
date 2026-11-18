import streamlit as st
import pandas as pd
import urllib.parse
import re
import os
import random
from datetime import datetime
from fpdf import FPDF

# Configuración general de la tienda
st.set_page_config(
    page_title="Mary's Store Ec & Babayork Urban | Tienda Oficial",
    page_icon="👠",
    layout="wide"
)

# Estilos CSS inspirados exactamente en el diseño Deprati aprobado
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }
    .top-utility-bar {
        display: flex;
        justify-content: flex-end;
        gap: 20px;
        font-size: 0.78rem;
        color: #4b5563;
        border-bottom: 1px solid #f3f4f6;
        padding-bottom: 6px;
        margin-bottom: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .top-utility-highlight {
        color: #e11d48;
        font-weight: 700;
    }
    .category-banner-black {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 18px 28px;
        font-size: 1.65rem;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    .breadcrumbs {
        font-size: 0.8rem;
        color: #9ca3af;
        text-transform: uppercase;
        margin-bottom: 18px;
        letter-spacing: 0.5px;
    }
    .product-img-wrapper {
        position: relative;
        background-color: #f9fafb;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 10px;
        text-align: center;
    }
    .product-img-wrapper img {
        width: 100%;
        height: 270px;
        object-fit: cover;
        display: block;
        transition: transform 0.3s ease;
    }
    .product-img-wrapper img:hover {
        transform: scale(1.03);
    }
    .badge-discount {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: #e11d48;
        color: #ffffff;
        padding: 4px 9px;
        font-size: 0.78rem;
        font-weight: 700;
        border-radius: 2px;
        z-index: 2;
    }
    .badge-new {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background-color: #7c7c7c;
        color: #ffffff;
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        z-index: 2;
    }
    .product-title {
        font-size: 0.98rem;
        color: #1f2937;
        font-weight: 600;
        margin: 4px 0 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .product-sub {
        font-size: 0.8rem;
        color: #6b7280;
        margin-bottom: 6px;
    }
    .price-offer {
        color: #e11d48;
        font-size: 1.25rem;
        font-weight: 800;
        margin-right: 8px;
    }
    .price-regular {
        text-decoration: line-through;
        color: #9ca3af;
        font-size: 0.92rem;
    }
    .price-wholesale {
        background-color: #fffbeb;
        border: 1px solid #fde68a;
        color: #b45309;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .stock-ok {
        color: #059669;
        font-size: 0.82rem;
        font-weight: 700;
        background: #ecfdf5;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .stock-zero {
        color: #dc2626;
        font-size: 0.82rem;
        font-weight: 700;
        background: #fef2f2;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .sidebar-filter-title {
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: #111827;
        border-bottom: 2px solid #111827;
        padding-bottom: 6px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    .payment-box-detail {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px;
        background-color: #ffffff;
        margin: 14px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .whatsapp-btn {
        display: block;
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 14px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.05rem;
        margin-top: 12px;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.25);
    }
    .card-btn {
        display: block;
        background-color: #1d4ed8;
        color: white !important;
        text-align: center;
        padding: 14px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.05rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar variables de estado
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "vista_actual" not in st.session_state:
    st.session_state.vista_actual = "DETAL"
if "cat_menu" not in st.session_state:
    st.session_state.cat_menu = "TODAS"
if "producto_seleccionado" not in st.session_state:
    st.session_state.producto_seleccionado = None
if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None
if "orden_confirmada" not in st.session_state:
    st.session_state.orden_confirmada = None
if "cliente_autocompletado" not in st.session_state:
    st.session_state.cliente_autocompletado = {}

# Diccionario completo de Provincias y Cantones del Ecuador
PROVINCIAS_CANTONES_EC = {
    "Los Ríos": ["Babahoyo", "Quevedo", "Ventanas", "Vinces", "Buena Fe", "Valencia", "Montalvo", "Urdaneta", "Baba", "Palenque", "Puebloviejo", "Mocache", "Quinsaloma"],
    "Guayas": ["Guayaquil", "Samborondón", "Daule", "Durán", "Milagro", "Playas", "Naranjal", "El Triunfo", "Balzar", "Yaguachi", "Salitre", "Pedro Carbo", "Naranjito"],
    "Pichincha": ["Quito", "Rumiñahui (Sangolquí)", "Cayambe", "Mejía (Machachi)", "Pedro Moncayo", "Puerto Quito", "San Miguel de los Bancos", "Pedro Vicente Maldonado"],
    "Azuay": ["Cuenca", "Gualaceo", "Paute", "Santa Isabel", "Sigsig", "Girón", "Camilo Ponce Enríquez"],
    "Manabí": ["Portoviejo", "Manta", "Chone", "Montecristi", "Jipijapa", "El Carmen", "Bahía de Caráquez", "Pedernales"],
    "El Oro": ["Machala", "Pasaje", "Santa Rosa", "Huaquillas", "El Guabo", "Piñas", "Zaruma"],
    "Tungurahua": ["Ambato", "Baños de Agua Santa", "Pelileo", "Píllaro", "Cevallos"],
    "Santo Domingo de los Tsáchilas": ["Santo Domingo", "La Concordia"],
    "Esmeraldas": ["Esmeraldas", "Atacames", "Quinindé", "San Lorenzo", "Muisne"],
    "Santa Elena": ["Santa Elena", "La Libertad", "Salinas"],
    "Imbabura": ["Ibarra", "Otavalo", "Cotacachi", "Antonio Ante"],
    "Loja": ["Loja", "Catamayo", "Cariamanga", "Macará"],
    "Chimborazo": ["Riobamba", "Guano", "Alausí", "Cumandá"],
    "Cotopaxi": ["Latacunga", "Salcedo", "La Maná", "Pujilí"],
    "Carchi": ["Tulcán", "Montúfar", "Espejo"],
    "Bolívar": ["Guaranda", "San Miguel", "Caluma", "Echeandía"],
    "Cañar": ["Azogues", "La Troncal", "Cañar"],
    "Pastaza": ["Puyo", "Mera", "Santa Clara"],
    "Morona Santiago": ["Macas", "Gualaquiza", "Sucúa"],
    "Napo": ["Tena", "Archidona", "El Chaco"],
    "Orellana": ["Francisco de Orellana (El Coca)", "La Joya de los Sachas"],
    "Sucumbíos": ["Nueva Loja (Lago Agrio)", "Shushufindi"],
    "Zamora Chinchipe": ["Zamora", "Yantzaza"],
    "Galápagos": ["Santa Cruz", "San Cristóbal", "Isabela"]
}

# Funciones seguras de limpieza
def limpiar_numero_float(valor, por_defecto=0.0):
    if pd.isna(valor):
        return float(por_defecto)
    texto = str(valor).strip()
    if not texto:
        return float(por_defecto)
    texto = re.sub(r"[^0-9,.-]", "", texto)
    if "," in texto and "." not in texto:
        texto = texto.replace(",", ".")
    elif "," in texto and "." in texto:
        texto = texto.replace(",", "")
    try:
        return float(texto)
    except Exception:
        return float(por_defecto)

def limpiar_numero_int(valor, por_defecto=0):
    return int(round(limpiar_numero_float(valor, por_defecto)))

def preparar_url_imagen(url):
    if pd.isna(url) or not str(url).strip():
        return "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"
    url_str = str(url).strip()
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url_str)
    if not match:
        match = re.search(r"id=([a-zA-Z0-9_-]+)", url_str)
    if match and "drive.google.com" in url_str:
        file_id = match.group(1)
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w800"
    return url_str

# Función para generar Nota de Pedido en PDF
def generar_pdf_pedido(num_orden, fecha_str, cliente_info, carrito, total_pares, subtotal, envio, recargo_pp, total):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "MARY'S STORE EC & BABAYORK URBAN", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Tienda Oficial de Calzado | WhatsApp: 0959276539", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"NOTA DE PEDIDO: #{num_orden}  |  Fecha: {fecha_str}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    def limpiar_texto(txt):
        return str(txt).encode("latin-1", "replace").decode("latin-1")

    pdf.cell(0, 6, limpiar_texto(f"Cliente: {cliente_info['nombres']} {cliente_info['apellidos']} (C.I.: {cliente_info['cedula']})"), ln=True)
    pdf.cell(0, 6, limpiar_texto(f"Celular: {cliente_info['celular']}"), ln=True)
    pdf.cell(0, 6, limpiar_texto(f"Ubicacion: Ecuador - {cliente_info['provincia']} - {cliente_info['canton']}"), ln=True)
    pdf.cell(0, 6, limpiar_texto(f"Direccion Exacta: {cliente_info['direccion']}"), ln=True)
    pdf.cell(0, 6, limpiar_texto(f"Metodo de Envio: {cliente_info['courier']}"), ln=True)
    pdf.cell(0, 6, limpiar_texto(f"Forma de Pago: {cliente_info['metodo_pago']}"), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(65, 8, "Modelo", 1, 0, "L", True)
    pdf.cell(45, 8, "Color", 1, 0, "C", True)
    pdf.cell(20, 8, "Talla", 1, 0, "C", True)
    pdf.cell(20, 8, "Cant.", 1, 0, "C", True)
    pdf.cell(40, 8, "Subtotal", 1, 1, "R", True)
    
    pdf.set_font("Helvetica", "", 10)
    for item in carrito:
        p_u = item["precio_may"] if total_pares >= item["min_may"] else item["precio_ofe"]
        sub_i = round(p_u * item["cantidad"], 2)
        pdf.cell(65, 8, limpiar_texto(item["modelo"])[:28], 1, 0, "L")
        pdf.cell(45, 8, limpiar_texto(item["color"])[:20], 1, 0, "C")
        pdf.cell(20, 8, limpiar_texto(item["talla"]), 1, 0, "C")
        pdf.cell(20, 8, str(item["cantidad"]), 1, 0, "C")
        pdf.cell(40, 8, f"${sub_i:.2f}", 1, 1, "R")
        
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(150, 7, "Subtotal Calzado:", 0, 0, "R")
    pdf.cell(40, 7, f"${subtotal:.2f}", 0, 1, "R")
    pdf.cell(150, 7, "Costo de Envio:", 0, 0, "R")
    pdf.cell(40, 7, f"${envio:.2f}", 0, 1, "R")
    if recargo_pp > 0:
        pdf.cell(150, 7, "Comision Pasarela Tarjeta (6%):", 0, 0, "R")
        pdf.cell(40, 7, f"${recargo_pp:.2f}", 0, 1, "R")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(150, 9, "TOTAL A PAGAR:", 0, 0, "R")
    pdf.cell(40, 9, f"${total:.2f}", 0, 1, "R")
    
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, limpiar_texto("Importante: Este documento respalda el detalle de tu pedido. El despacho se realiza una vez confirmado el comprobante de pago en nuestro WhatsApp 0959276539."))
    
    return bytes(pdf.output())

# Conexión en vivo con Google Sheets
SHEET_ID = "1LGRa-BfRkiRbyqukW0aWWpHJh2tKV_W-IgB0SRbx8N0"
URL_INV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Inventario"
URL_CLI = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Fidelidad_Clientes"
URL_ENV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Costos_Envio"
URL_PED = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Ventas_Historial"

@st.cache_data(ttl=15)
def cargar_sheet(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

df_inv = cargar_sheet(URL_INV)
if df_inv.empty or "Modelo" not in df_inv.columns:
    respaldo = [
        {"ID_Variante": 1, "Modelo": "Edilma", "Categoría": "Baletas", "Material": "Cuero - Gamusa", "Color": "Beige", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 14.50, "Mínimo Mayorista": 6, "En Oferta": "Si", "Talla 34": 2, "Talla 35": 3, "Talla 36": 5, "Talla 37": 4, "Talla 38": 3, "Talla 39": 2, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"},
        {"ID_Variante": 2, "Modelo": "Edilma", "Categoría": "Baletas", "Material": "Cuero - Gamusa", "Color": "Rojo", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 14.50, "Mínimo Mayorista": 6, "En Oferta": "Si", "Talla 34": 0, "Talla 35": 2, "Talla 36": 4, "Talla 37": 3, "Talla 38": 2, "Talla 39": 0, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111"},
        {"ID_Variante": 3, "Modelo": "Lunita", "Categoría": "Sandalias", "Material": "Charol", "Color": "Negro", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 14.50, "Mínimo Mayorista": 6, "En Oferta": "Si", "Talla 34": 1, "Talla 35": 2, "Talla 36": 3, "Talla 37": 4, "Talla 38": 2, "Talla 39": 1, "Talla 40": 0, "Enlace Imagen": "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95"},
        {"ID_Variante": 4, "Modelo": "Flats Cadena", "Categoría": "Baletas", "Material": "Cuero", "Color": "Negro", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 15.00, "Mínimo Mayorista": 6, "En Oferta": "Si", "Talla 34": 2, "Talla 35": 3, "Talla 36": 4, "Talla 37": 4, "Talla 38": 3, "Talla 39": 2, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a"}
    ]
    df_inv = pd.DataFrame(respaldo)

if "En Oferta" not in df_inv.columns:
    df_inv["En Oferta"] = "Si"

df_envios = cargar_sheet(URL_ENV)
df_cli = cargar_sheet(URL_CLI)
df_ped = cargar_sheet(URL_PED)

total_items_carrito = sum(item["cantidad"] for item in st.session_state.carrito)

# ==============================================================================
# 1. CABECERA EXACTA A LA CAPTURA APROBADA
# ==============================================================================
st.markdown("""
<div class="top-utility-bar">
    <span>🚚 ENVÍOS A TODO EL ECUADOR</span>
    <span>|</span>
    <span>📍 PAGO CONTRAENTREGA EN BABAHOYO</span>
    <span>|</span>
    <span class="top-utility-highlight">⭐ CLUB DE FIDELIDAD & MAYORISTAS: 0959276539</span>
</div>
""", unsafe_allow_html=True)

h_col_logos, h_col_search, h_col_actions = st.columns([2.2, 4.1, 2.7], vertical_alignment="center")

with h_col_logos:
    l1, l2 = st.columns(2, vertical_alignment="center")
    with l1:
        if os.path.exists("logo_marys.jpg"):
            st.image("logo_marys.jpg", width=130)
        elif os.path.exists("logo_marys.png"):
            st.image("logo_marys.png", width=130)
        else:
            st.markdown("<h3 style='margin:0; font-family:serif;'>Mary's Store Ec</h3>", unsafe_allow_html=True)
    with l2:
        if os.path.exists("logo_babayork.jpg"):
            st.image("logo_babayork.jpg", width=95)
        elif os.path.exists("logo_babayork.png"):
            st.image("logo_babayork.png", width=95)
        else:
            st.markdown("<h4 style='margin:0; letter-spacing:1px;'>BABAYORK URBAN</h4>", unsafe_allow_html=True)

with h_col_search:
    busqueda = st.text_input(
        "Buscar producto",
        placeholder="🔍 Busca tu zapato por modelo, color o material (ej. Edilma, Charol, Deportivo)...",
        label_visibility="collapsed"
    )

with h_col_actions:
    ac1, ac2, ac3 = st.columns([1, 1.1, 1.2])
    with ac1:
        if st.button("👤 Mi Cuenta", use_container_width=True, type="primary" if st.session_state.vista_actual == "LOGIN" else "secondary"):
            st.session_state.producto_seleccionado = None
            st.session_state.vista_actual = "LOGIN"
            st.rerun()
    with ac2:
        if st.button("📦 Mayoristas", use_container_width=True, type="primary" if st.session_state.vista_actual == "MAYORISTA" else "secondary"):
            st.session_state.producto_seleccionado = None
            st.session_state.vista_actual = "MAYORISTA"
            st.rerun()
    with ac3:
        if st.button(f"🛍️ Mi Carrito ({total_items_carrito})", use_container_width=True, type="primary"):
            st.session_state.producto_seleccionado = None
            st.session_state.vista_actual = "CARRITO"
            st.rerun()

# ==============================================================================
# 2. MENÚ HORIZONTAL DE CATEGORÍAS (ESTILO DEPRATI EXACTO)
# ==============================================================================
st.markdown("<hr style='margin: 8px 0; border-color: #e5e7eb;'>", unsafe_allow_html=True)

categorias_base = sorted([str(c).strip() for c in df_inv["Categoría"].dropna().unique() if str(c).strip()])
opciones_menu = ["TODAS"] + [c.upper() for c in categorias_base] + ["🔥 REBAJAS / MAYORISTA", "ℹ️ INFO & FIDELIDAD", "🛒 IR A PAGAR"]

cols_nav = st.columns(len(opciones_menu))
for i, opcion in enumerate(opciones_menu):
    with cols_nav[i]:
        es_activo = (
            (opcion == "🛒 IR A PAGAR" and st.session_state.vista_actual == "CARRITO" and st.session_state.producto_seleccionado is None) or
            (opcion == "ℹ️ INFO & FIDELIDAD" and st.session_state.vista_actual == "INFO" and st.session_state.producto_seleccionado is None) or
            (opcion == "🔥 REBAJAS / MAYORISTA" and st.session_state.vista_actual == "MAYORISTA" and st.session_state.producto_seleccionado is None) or
            (st.session_state.vista_actual == "DETAL" and st.session_state.cat_menu == opcion and st.session_state.producto_seleccionado is None)
        )
        if st.button(opcion, key=f"nav_btn_{i}", use_container_width=True, type="primary" if es_activo else "secondary"):
            st.session_state.producto_seleccionado = None
            if opcion == "🛒 IR A PAGAR":
                st.session_state.vista_actual = "CARRITO"
            elif opcion == "ℹ️ INFO & FIDELIDAD":
                st.session_state.vista_actual = "INFO"
            elif opcion == "🔥 REBAJAS / MAYORISTA":
                st.session_state.vista_actual = "MAYORISTA"
                st.session_state.cat_menu = "TODAS"
            else:
                st.session_state.vista_actual = "DETAL"
                st.session_state.cat_menu = opcion
            st.rerun()

# ==============================================================================
# VISTA DE DETALLE INDIVIDUAL DE ARTÍCULO (AL HACER CLIC EN VER DETALLE)
# ==============================================================================
if st.session_state.producto_seleccionado is not None:
    nombre_mod_sel = st.session_state.producto_seleccionado["modelo"]
    color_inicial = st.session_state.producto_seleccionado.get("color", None)
    
    st.markdown(f'<div class="category-banner-black">DETALLE DEL ARTÍCULO: {nombre_mod_sel}</div>', unsafe_allow_html=True)
    
    top_d1, top_d2 = st.columns([3, 1])
    with top_d1:
        if st.button("⬅️ Volver al Catálogo Principal"):
            st.session_state.producto_seleccionado = None
            st.rerun()
    with top_d2:
        if st.button(f"🛍️ Ir al Carrito ({total_items_carrito})", use_container_width=True, type="primary"):
            st.session_state.producto_seleccionado = None
            st.session_state.vista_actual = "CARRITO"
            st.rerun()

    variantes_prod = df_inv[df_inv["Modelo"] == nombre_mod_sel]
    if variantes_prod.empty:
        st.session_state.producto_seleccionado = None
        st.rerun()
        
    col_foto_grande, col_especificaciones = st.columns([1.1, 1.2], gap="large")
    
    with col_especificaciones:
        fila_base = variantes_prod.iloc[0]
        cat_prod = str(fila_base.get("Categoría", "Calzado")).strip()
        mat_prod = str(fila_base.get("Material", "Cuero / Sintético")).strip()
        id_var = str(fila_base.get("ID_Variante", "001")).strip()
        
        st.markdown(f"<h2 style='margin-bottom:2px; color:#111827;'>{nombre_mod_sel}</h2>", unsafe_allow_html=True)
        st.caption(f"Código: **MB-00{id_var}** | Categoría: **{cat_prod}** | Marca: **Mary's Store Ec / Babayork Urban**")
        
        colores_disponibles = list(variantes_prod["Color"].dropna().unique())
        idx_col = colores_disponibles.index(color_inicial) if (color_inicial in colores_disponibles) else 0
        
        sc1, sc2 = st.columns(2)
        with sc1:
            color_sel_det = st.selectbox("🎨 COLOR *", colores_disponibles, index=idx_col, key="det_color_sel")
        with sc2:
            talla_sel_det = st.selectbox("📏 TALLA *", ["34", "35", "36", "37", "38", "39", "40"], index=2, key="det_talla_sel")
            
        filas_color_det = variantes_prod[variantes_prod["Color"] == color_sel_det]
        fila_activa = filas_color_det.iloc[0] if not filas_color_det.empty else fila_base
        
        p_reg_d = limpiar_numero_float(fila_activa.get("Precio Regular ($)", 24.99), 24.99)
        p_ofe_d = limpiar_numero_float(fila_activa.get("Precio Oferta ($)", 19.99), 19.99)
        p_may_d = limpiar_numero_float(fila_activa.get("Precio Mayorista ($)", p_ofe_d * 0.75), round(p_ofe_d * 0.75, 2))
        min_may_d = max(1, limpiar_numero_int(fila_activa.get("Mínimo Mayorista", 6), 6))
        en_oferta_d = str(fila_activa.get("En Oferta", "Si")).strip().lower() in ["si", "sí", "yes", "true", "1"]
        
        precio_base_det = p_ofe_d if en_oferta_d else p_reg_d
        precio_payphone_det = round(precio_base_det * 1.06, 2)
        
        # Caja comparativa de precios estilo captura adjunta (Transferencia vs Tarjeta PayPhone)
        st.markdown(f"""
        <div class="payment-box-detail">
            <div style="font-size:0.78rem; color:#0284c7; font-weight:700; text-transform:uppercase; margin-bottom:8px;">
                MÉTODOS DE PAGO Y PRECIOS
            </div>
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="flex:1; padding-right:14px; border-right:2px solid #111827;">
                    <div style="font-size:0.95rem; font-weight:700; color:#111827;">Transferencia / Efectivo</div>
                    <div style="font-size:1.55rem; font-weight:800; color:#e11d48;">${precio_base_det:.2f}</div>
                    <div style="font-size:0.75rem; color:#6b7280;">Sin recargo • Mayorista: ${p_may_d:.2f} ({min_may_d}+ pares)</div>
                </div>
                <div style="flex:1; padding-left:16px;">
                    <div style="font-size:0.95rem; font-weight:700; color:#111827;">Tarjeta de Crédito (PayPhone)</div>
                    <div style="font-size:1.55rem; font-weight:800; color:#111827;">${precio_payphone_det:.2f}</div>
                    <div style="font-size:0.75rem; color:#6b7280;">Incluye 5% + IVA (6% comisión pasarela)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_talla_key = f"Talla {talla_sel_det}"
        stock_det = limpiar_numero_int(fila_activa.get(col_talla_key, 0), 0) if col_talla_key in fila_activa else 5
        url_img_det = preparar_url_imagen(fila_activa.get("Enlace Imagen"))
        
        if stock_det > 0:
            st.markdown(f"<div class='stock-ok'>✅ Disponible en color {color_sel_det} y talla {talla_sel_det} ({stock_det} pares en stock)</div>", unsafe_allow_html=True)
            cd1, cd2 = st.columns([1, 2], vertical_alignment="bottom")
            with cd1:
                cant_det = st.number_input("Cantidad:", min_value=1, max_value=stock_det, value=1, step=1, key="det_cant_input")
            with cd2:
                if st.button("🛒 AÑADIR AL CARRITO", type="primary", use_container_width=True, key="det_add_btn"):
                    st.session_state.carrito.append({
                        "modelo": nombre_mod_sel,
                        "categoria": cat_prod,
                        "color": str(color_sel_det),
                        "talla": str(talla_sel_det),
                        "cantidad": int(cant_det),
                        "precio_unitario": float(precio_base_det),
                        "precio_ofe": float(precio_base_det),
                        "precio_may": float(p_may_d),
                        "min_may": int(min_may_d),
                        "subtotal": round(int(cant_det) * float(precio_base_det), 2),
                        "imagen": url_img_det
                    })
                    st.session_state.orden_confirmada = None
                    st.toast(f"✅ {nombre_mod_sel} ({color_sel_det} - Talla {talla_sel_det}) añadido al carrito.")
                    st.rerun()
        else:
            st.markdown(f"<div class='stock-zero'>❌ Agotado en color {color_sel_det} y talla {talla_sel_det} (Stock: 0)</div>", unsafe_allow_html=True)
            
        st.markdown("#### Características del Calzado:")
        st.markdown(f"""
        - **Modelo:** {nombre_mod_sel}
        - **Color seleccionado:** {color_sel_det}
        - **Material:** {mat_prod} de alta durabilidad y confort
        - **Tallas disponibles:** Horma nacional (34 al 40)
        - **Envíos:** A todo el Ecuador por Servientrega o Cooperativa, y contraentrega en Babahoyo.
        """)
        
        with st.expander("📏 Guía de Tallas de Calzado (Ecuador / Centímetros)", expanded=True):
            st.markdown("""
            | Talla Ecuador (EU) | Largo del Pie (cm) | Equivalencia US Mujer |
            | :---: | :---: | :---: |
            | **34** | 22.0 - 22.5 cm | 5.0 |
            | **35** | 22.6 - 23.0 cm | 5.5 |
            | **36** | 23.1 - 23.5 cm | 6.0 |
            | **37** | 23.6 - 24.0 cm | 6.5 - 7.0 |
            | **38** | 24.1 - 24.5 cm | 7.5 |
            | **39** | 24.6 - 25.5 cm | 8.0 - 8.5 |
            | **40** | 25.6 - 26.0 cm | 9.0 |
            """)

    with col_foto_grande:
        porcentaje_d = int(round(((p_reg_d - p_ofe_d) / p_reg_d) * 100)) if (en_oferta_d and p_reg_d > p_ofe_d and p_reg_d > 0) else 0
        badge_d_html = f'<span class="badge-discount">-{porcentaje_d}%</span>' if porcentaje_d > 0 else ''
        st.markdown(
            f'<div class="product-img-wrapper" style="height:440px;">'
            f'{badge_d_html}<span class="badge-new">NUEVO</span>'
            f'<img src="{url_img_det}" style="height:440px; object-fit:cover;">'
            f'</div>',
            unsafe_allow_html=True
        )

# ==============================================================================
# VISTA DE CATÁLOGO PRINCIPAL (100% FIEL A LA CAPTURA DEPRATI APROBADA)
# ==============================================================================
elif st.session_state.vista_actual in ["DETAL", "MAYORISTA"]:
    es_mayorista = (st.session_state.vista_actual == "MAYORISTA")
    titulo_banner = "ZONA MAYORISTA Y REBAJAS POR TEMPORADA" if es_mayorista else (
        "COLECCIÓN COMPLETA DE CALZADO" if st.session_state.cat_menu == "TODAS" else st.session_state.cat_menu
    )
    
    st.markdown(f'<div class="category-banner-black">{titulo_banner}</div>', unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns([3, 1], vertical_alignment="center")
    with b_col1:
        st.markdown(f'<div class="breadcrumbs">HOME &gt; CALZADO &gt; {titulo_banner}</div>', unsafe_allow_html=True)
    with b_col2:
        orden_elegido = st.selectbox(
            "Ordenar por",
            ["Ordenar: Destacados", "Precio: Menor a Mayor", "Precio: Mayor a Menor", "Nombre: A - Z"],
            label_visibility="collapsed"
        )

    if es_mayorista:
        st.info("📦 **Modo Mayorista Activo:** Precios especiales por volumen (combinando tallas y colores) directamente desde la fábrica/proveedor.")

    # Layout exacto: Columna izquierda de Filtros y Columna derecha con Grilla de 3 Productos
    col_sidebar, col_catalogo = st.columns([1.15, 3.85], gap="large")

    with col_sidebar:
        st.markdown('<div class="sidebar-filter-title">FILTROS</div>', unsafe_allow_html=True)
        
        with st.expander("CATEGORÍAS", expanded=True):
            cat_opciones = ["TODAS"] + [c.upper() for c in categorias_base]
            idx_cat = cat_opciones.index(st.session_state.cat_menu) if st.session_state.cat_menu in cat_opciones else 0
            cat_filtro_side = st.radio("Selecciona categoría:", cat_opciones, index=idx_cat, label_visibility="collapsed")
            if cat_filtro_side != st.session_state.cat_menu:
                st.session_state.cat_menu = cat_filtro_side
                st.rerun()

        with st.expander("TALLA DISPONIBLE", expanded=True):
            talla_filtro = st.selectbox("Ver stock en talla:", ["Todas las tallas", "34", "35", "36", "37", "38", "39", "40"], label_visibility="collapsed")

        with st.expander("COLOR", expanded=False):
            colores_unicos = ["Todos"] + sorted([str(c).strip() for c in df_inv["Color"].dropna().unique() if str(c).strip()])
            color_filtro = st.selectbox("Filtrar por color:", colores_unicos, label_visibility="collapsed")

        with st.expander("MATERIAL", expanded=False):
            materiales_unicos = ["Todos"] + sorted([str(m).strip() for m in df_inv["Material"].dropna().unique() if str(m).strip()])
            material_filtro = st.selectbox("Filtrar por material:", materiales_unicos, label_visibility="collapsed")

        solo_con_stock = st.checkbox("Solo con stock disponible", value=False)
        solo_descuentos = st.checkbox("Solo ofertas / descuentos", value=False)

    with col_catalogo:
        df_mostrar = df_inv.copy()
        
        if st.session_state.cat_menu != "TODAS":
            df_mostrar = df_mostrar[df_mostrar["Categoría"].astype(str).str.upper().str.strip() == st.session_state.cat_menu]
        if busqueda:
            df_mostrar = df_mostrar[
                df_mostrar["Modelo"].astype(str).str.contains(busqueda, case=False, na=False) |
                df_mostrar["Material"].astype(str).str.contains(busqueda, case=False, na=False) |
                df_mostrar["Color"].astype(str).str.contains(busqueda, case=False, na=False)
            ]
        if color_filtro != "Todos":
            df_mostrar = df_mostrar[df_mostrar["Color"].astype(str).str.strip() == color_filtro]
        if material_filtro != "Todos":
            df_mostrar = df_mostrar[df_mostrar["Material"].astype(str).str.strip() == material_filtro]
        if solo_descuentos and "En Oferta" in df_mostrar.columns:
            df_mostrar = df_mostrar[df_mostrar["En Oferta"].astype(str).str.strip().str.lower().isin(["si", "sí", "yes", "true", "1"])]

        modelos_unicos = list(df_mostrar["Modelo"].dropna().unique())
        
        if orden_elegido == "Nombre: A - Z":
            modelos_unicos = sorted(modelos_unicos)
        elif orden_elegido in ["Precio: Menor a Mayor", "Precio: Mayor a Menor"]:
            reverso = (orden_elegido == "Precio: Mayor a Menor")
            modelos_unicos = sorted(
                modelos_unicos,
                key=lambda m: limpiar_numero_float(df_mostrar[df_mostrar["Modelo"] == m].iloc[0].get("Precio Oferta ($)", 19.99), 19.99),
                reverse=reverso
            )

        if len(modelos_unicos) == 0:
            st.warning("No se encontraron zapatos con esos filtros. Intenta cambiar la categoría o desmarcar algún filtro.")
        else:
            cols_grid = st.columns(3, gap="medium")
            tarjeta_idx = 0
            
            for idx, nombre_modelo in enumerate(modelos_unicos):
                variantes_modelo = df_mostrar[df_mostrar["Modelo"] == nombre_modelo]
                if variantes_modelo.empty:
                    continue
                
                with cols_grid[tarjeta_idx % 3]:
                    with st.container(border=True):
                        primera_fila = variantes_modelo.iloc[0]
                        categoria_mod = str(primera_fila.get("Categoría", "Calzado")).strip()
                        material_mod = str(primera_fila.get("Material", "Estándar")).strip()
                        
                        colores_disp = list(variantes_modelo["Color"].dropna().unique())
                        if not colores_disp:
                            colores_disp = ["Único"]
                            
                        foto_placeholder = st.empty()
                        btn_detalle_placeholder = st.empty()
                        
                        st.markdown(f'<div class="product-title">{nombre_modelo}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="product-sub">{categoria_mod} • {material_mod}</div>', unsafe_allow_html=True)
                        
                        sel_c1, sel_c2 = st.columns(2)
                        with sel_c1:
                            color_elegido = st.selectbox(
                                "🎨 Color",
                                colores_disp,
                                key=f"color_{nombre_modelo}_{idx}"
                            )
                        with sel_c2:
                            tallas_lista = ["34", "35", "36", "37", "38", "39", "40"]
                            idx_talla_def = tallas_lista.index(talla_filtro) if talla_filtro in tallas_lista else 2
                            talla_elegida = st.selectbox(
                                "📏 Talla",
                                tallas_lista,
                                index=idx_talla_def,
                                key=f"talla_{nombre_modelo}_{idx}"
                            )
                        
                        filas_coincidentes = variantes_modelo[variantes_modelo["Color"] == color_elegido]
                        fila_color = filas_coincidentes.iloc[0] if not filas_coincidentes.empty else primera_fila
                        
                        p_reg = limpiar_numero_float(fila_color.get("Precio Regular ($)", 24.99), 24.99)
                        p_ofe = limpiar_numero_float(fila_color.get("Precio Oferta ($)", 19.99), 19.99)
                        p_may = limpiar_numero_float(fila_color.get("Precio Mayorista ($)", p_ofe * 0.75), round(p_ofe * 0.75, 2))
                        min_may = max(1, limpiar_numero_int(fila_color.get("Mínimo Mayorista", 6), 6))
                        en_oferta = str(fila_color.get("En Oferta", "Si")).strip().lower() in ["si", "sí", "yes", "true", "1"]
                        
                        if en_oferta and p_reg > p_ofe and p_reg > 0:
                            porcentaje_desc = int(round(((p_reg - p_ofe) / p_reg) * 100))
                        else:
                            porcentaje_desc = 0
                            
                        url_limpia = preparar_url_imagen(fila_color.get("Enlace Imagen"))
                        badge_html = f'<span class="badge-discount">-{porcentaje_desc}%</span>' if porcentaje_desc > 0 else ''
                        
                        # HTML en una sola línea para evitar que Markdown lo interprete como bloque de código
                        foto_placeholder.markdown(
                            f'<div class="product-img-wrapper">{badge_html}<span class="badge-new">NUEVO</span><img src="{url_limpia}" alt="{nombre_modelo}"></div>',
                            unsafe_allow_html=True
                        )
                        
                        if btn_detalle_placeholder.button("🔍 Ver Ficha Completa y Guía de Tallas", key=f"ver_det_{nombre_modelo}_{idx}", use_container_width=True):
                            st.session_state.producto_seleccionado = {
                                "modelo": nombre_modelo,
                                "color": color_elegido
                            }
                            st.rerun()
                        
                        if es_mayorista:
                            st.markdown(f"<span class='price-offer'>${p_may:.2f}</span> <span class='price-regular'>${p_ofe:.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"<div class='price-wholesale'>📦 Mayorista desde {min_may} pares</div>", unsafe_allow_html=True)
                            precio_aplicado = p_may
                        else:
                            if en_oferta and p_reg > p_ofe:
                                st.markdown(f"<span class='price-offer'>${p_ofe:.2f}</span> <span class='price-regular'>${p_reg:.2f}</span>", unsafe_allow_html=True)
                                precio_aplicado = p_ofe
                            else:
                                st.markdown(f"<span class='price-offer'>${p_reg:.2f}</span>", unsafe_allow_html=True)
                                precio_aplicado = p_reg
                            st.markdown(f"<div class='price-wholesale'>💡 Mayorista: ${p_may:.2f} ({min_may}+ pares)</div>", unsafe_allow_html=True)

                        col_talla_nombre = f"Talla {talla_elegida}"
                        stock_disponible = limpiar_numero_int(fila_color.get(col_talla_nombre, 0), 0) if col_talla_nombre in fila_color else 5
                        
                        if stock_disponible > 0:
                            st.markdown(f"<div class='stock-ok'>✅ Stock disponible: {stock_disponible} pares</div>", unsafe_allow_html=True)
                            cant_min = min_may if (es_mayorista and stock_disponible >= min_may) else 1
                            
                            c_cant, c_btn = st.columns([1, 1.6], vertical_alignment="bottom")
                            with c_cant:
                                cantidad_pedir = st.number_input(
                                    "Cant.",
                                    min_value=1,
                                    max_value=stock_disponible,
                                    value=min(cant_min, stock_disponible),
                                    step=1,
                                    key=f"cant_{nombre_modelo}_{idx}"
                                )
                            with c_btn:
                                if st.button("🛒 Agregar", key=f"btn_{nombre_modelo}_{idx}", use_container_width=True, type="primary"):
                                    st.session_state.carrito.append({
                                        "modelo": nombre_modelo,
                                        "categoria": categoria_mod,
                                        "color": str(color_elegido),
                                        "talla": str(talla_elegida),
                                        "cantidad": int(cantidad_pedir),
                                        "precio_unitario": float(precio_aplicado),
                                        "precio_ofe": float(precio_aplicado),
                                        "precio_may": float(p_may),
                                        "min_may": int(min_may),
                                        "subtotal": round(int(cantidad_pedir) * float(precio_aplicado), 2),
                                        "imagen": url_limpia
                                    })
                                    st.session_state.orden_confirmada = None
                                    st.toast(f"✅ {nombre_modelo} ({color_elegido} - Talla {talla_elegida}) agregado al carrito.")
                                    st.rerun()
                        else:
                            st.markdown("<div class='stock-zero'>❌ Agotado en este color y talla (0)</div>", unsafe_allow_html=True)
                            st.caption("Elige otro color u otra talla.")
                            
                tarjeta_idx += 1

# ==============================================================================
# VISTA 3: VENTANA DEL CARRITO, DATOS DE CLIENTE, PDF PERSISTENTE Y PAGO
# ==============================================================================
elif st.session_state.vista_actual == "CARRITO":
    st.markdown('<div class="category-banner-black">MI CARRITO Y FINALIZACIÓN DE COMPRA</div>', unsafe_allow_html=True)
    
    if st.button("⬅️ Seguir Comprando en el Catálogo"):
        st.session_state.vista_actual = "DETAL"
        st.rerun()
        
    if len(st.session_state.carrito) == 0:
        st.info("Tu carrito está vacío actualmente. Explora nuestro catálogo, elige color y talla y agrégalos a tu bolsa.")
    else:
        col_resumen, col_checkout = st.columns([1.1, 1.3], gap="large")
        
        with col_resumen:
            st.subheader("1. Resumen de tu Bolsa de Compras")
            total_pares_carrito = sum(item["cantidad"] for item in st.session_state.carrito)
            
            subtotal_general = 0.0
            for i, item in enumerate(st.session_state.carrito):
                if total_pares_carrito >= item["min_may"]:
                    precio_final_unit = item["precio_may"]
                    etiqueta_precio = "Precio Mayorista Aplicado"
                else:
                    precio_final_unit = item["precio_ofe"]
                    etiqueta_precio = "Precio Detal"
                
                subtotal_item = round(precio_final_unit * item["cantidad"], 2)
                subtotal_general += subtotal_item
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2.5, 1])
                    with c1:
                        st.image(item["imagen"], width=80)
                    with c2:
                        st.markdown(f"**{item['modelo']}** ({item['categoria']})")
                        st.write(f"🎨 Color: **{item['color']}** | 📏 Talla: **{item['talla']}**")
                        st.write(f"Cantidad: **{item['cantidad']}** x ${precio_final_unit:.2f} (*{etiqueta_precio}*)")
                    with c3:
                        st.markdown(f"**${subtotal_item:.2f}**")
                        if st.button("🗑️ Quitar", key=f"del_{i}"):
                            st.session_state.carrito.pop(i)
                            st.session_state.orden_confirmada = None
                            st.rerun()
            
            if st.button("🧹 Vaciar todo el carrito"):
                st.session_state.carrito = []
                st.session_state.orden_confirmada = None
                st.rerun()

        with col_checkout:
            st.subheader("2. Datos de Envío y Club de Fidelidad")
            
            # Buscador de Cédula para autocompletar
            c_busq1, c_busq2 = st.columns([2.5, 1], vertical_alignment="bottom")
            with c_busq1:
                ced_buscar = st.text_input("🪪 ¿Ya has comprado antes? Ingresa tu Cédula para autocompletar tus datos:", placeholder="Ej: 1204567890")
            with c_busq2:
                if st.button("🔍 Buscar Cédula", use_container_width=True):
                    if ced_buscar and not df_cli.empty and "Cédula" in df_cli.columns:
                        coincidencia = df_cli[df_cli["Cédula"].astype(str).str.strip() == str(ced_buscar).strip()]
                        if not coincidencia.empty:
                            fila_c = coincidencia.iloc[0]
                            nom_comp = str(fila_c.get("Nombres y Apellidos", "")).strip()
                            partes = nom_comp.split(" ", 1)
                            st.session_state.cliente_autocompletado = {
                                "cedula": str(ced_buscar).strip(),
                                "nombres": partes[0] if len(partes) > 0 else "",
                                "apellidos": partes[1] if len(partes) > 1 else "",
                                "celular": str(fila_c.get("Celular", "")),
                                "provincia": str(fila_c.get("Provincia", "Los Ríos")),
                                "canton": str(fila_c.get("Cantón", "Babahoyo")),
                                "direccion": str(fila_c.get("Dirección", fila_c.get("Dirección y Ciudad", "")))
                            }
                            st.success(f"✅ ¡Datos recuperados! Puntos acumulados: {fila_c.get('Puntos Fidelidad', 0)} pts.")
                        else:
                            st.info("Cédula nueva. Completa tus datos abajo para registrarte.")
                            st.session_state.cliente_autocompletado = {"cedula": str(ced_buscar).strip()}

            ca = st.session_state.cliente_autocompletado
            
            # Selectores de País, Provincia y Cantón fuera del form para actualización inmediata de cantones y tarifa de envío
            st.markdown("##### 🌍 Ubicación de Entrega")
            u_col1, u_col2, u_col3 = st.columns(3)
            with u_col1:
                st.selectbox("País", ["Ecuador"], disabled=True)
            with u_col2:
                lista_provincias = list(PROVINCIAS_CANTONES_EC.keys())
                idx_prov = lista_provincias.index(ca.get("provincia")) if ca.get("provincia") in lista_provincias else 0
                provincia_elegida = st.selectbox("Provincia *", lista_provincias, index=idx_prov)
            with u_col3:
                cantones_prov = PROVINCIAS_CANTONES_EC.get(provincia_elegida, ["Cantón Principal"])
                idx_cant = cantones_prov.index(ca.get("canton")) if ca.get("canton") in cantones_prov else 0
                canton_elegido = st.selectbox("Cantón / Ciudad *", cantones_prov, index=idx_cant)

            # Calcular costo de envío desde el Sheet Costos_Envio según Provincia y Cantón
            costo_envio_calc = 0.0 if (provincia_elegida == "Los Ríos" and canton_elegido == "Babahoyo") else 5.00
            if not df_envios.empty and "Provincia" in df_envios.columns and "Cantón" in df_envios.columns:
                match_env = df_envios[
                    (df_envios["Provincia"].astype(str).str.strip().str.lower() == provincia_elegida.lower()) &
                    (df_envios["Cantón"].astype(str).str.strip().str.lower() == canton_elegido.lower())
                ]
                if not match_env.empty:
                    costo_envio_calc = limpiar_numero_float(match_env.iloc[0].get("Costo ($)", 5.00), 5.00)

            st.caption(f"🚚 Tarifa de envío para **{canton_elegido} ({provincia_elegida})**: **${costo_envio_calc:.2f}**")

            with st.form("form_checkout"):
                cedula = st.text_input("🪪 Número de Cédula / RUC *", value=ca.get("cedula", ""))
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    nombres = st.text_input("👤 Nombres *", value=ca.get("nombres", ""))
                with col_n2:
                    apellidos = st.text_input("👤 Apellidos *", value=ca.get("apellidos", ""))
                
                celular = st.text_input("📱 Número de Celular (WhatsApp) *", value=ca.get("celular", ""))
                direccion = st.text_area("📍 Dirección exacta y referencia *", value=ca.get("direccion", ""))
                
                courier = st.selectbox(
                    "🚚 Empresa de Envío / Courier Preferido *",
                    [
                        f"Servientrega a domicilio / agencia (+${costo_envio_calc:.2f})",
                        f"Encargo en Cooperativa de Bus Interprovincial (+${costo_envio_calc:.2f})",
                        "Pago Contraentrega (Exclusivo dentro de Babahoyo - $0.00)"
                    ]
                )
                
                metodo_pago = st.radio(
                    "💳 Selecciona cómo deseas pagar:",
                    [
                        "Transferencia / Depósito Bancario (Sin recargo)",
                        "Pago en Línea con Tarjeta de Crédito / Débito - PayPhone (+6% comisión pasarela)",
                        "Efectivo Contraentrega (Solo Babahoyo)"
                    ]
                )
                
                guardar_fidelidad = st.checkbox("⭐ Deseo guardar mis datos para futuras compras y acumular puntos en el Club de Fidelidad", value=True)
                
                confirmar_btn = st.form_submit_button("✅ Confirmar Datos y Generar Orden de Compra", type="primary", use_container_width=True)

            if confirmar_btn:
                if not (cedula and nombres and apellidos and celular and direccion):
                    st.error("⚠️ Por favor completa todos los campos obligatorios (*) para continuar.")
                else:
                    envio_final = 0.0 if ("Babahoyo" in courier or canton_elegido == "Babahoyo") else costo_envio_calc
                    recargo_payphone = round(subtotal_general * 0.06, 2) if "PayPhone" in metodo_pago else 0.0
                    total_pagar = round(subtotal_general + envio_final + recargo_payphone, 2)
                    puntos_ganados = int(total_pares_carrito * 10)
                    
                    # Generar código único persistente en session_state para que NO se pierda al descargar el PDF
                    fecha_actual_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                    num_orden_unico = f"ORD-{datetime.now().strftime('%m%d')}-{random.randint(1000, 9999)}"
                    
                    lineas_productos = []
                    carrito_copia = []
                    for item in st.session_state.carrito:
                        p_u = item["precio_may"] if total_pares_carrito >= item["min_may"] else item["precio_ofe"]
                        sub_i = round(p_u * item["cantidad"], 2)
                        linea_txt = f"- {item['cantidad']}x {item['modelo']} (Color: {item['color']} | Talla: {item['talla']}) = ${sub_i:.2f}"
                        lineas_productos.append(linea_txt)
                        carrito_copia.append(dict(item))
                        
                    datos_cli = {
                        "cedula": cedula, "nombres": nombres, "apellidos": apellidos,
                        "celular": celular, "provincia": provincia_elegida, "canton": canton_elegido,
                        "direccion": direccion, "courier": courier, "metodo_pago": metodo_pago,
                        "guardar": guardar_fidelidad
                    }
                    
                    pdf_generado = generar_pdf_pedido(
                        num_orden_unico, fecha_actual_str, datos_cli, carrito_copia,
                        total_pares_carrito, subtotal_general, envio_final, recargo_payphone, total_pagar
                    )
                    
                    st.session_state.orden_confirmada = {
                        "num_orden": num_orden_unico,
                        "fecha": fecha_actual_str,
                        "datos_cli": datos_cli,
                        "lineas_productos": lineas_productos,
                        "total_pares": total_pares_carrito,
                        "subtotal": subtotal_general,
                        "envio": envio_final,
                        "recargo_pp": recargo_payphone,
                        "total": total_pagar,
                        "puntos": puntos_ganados,
                        "pdf_bytes": pdf_generado
                    }

            # Mostrar la Orden Confirmada de forma persistente (no desaparece al descargar el PDF)
            if st.session_state.orden_confirmada is not None:
                oc = st.session_state.orden_confirmada
                dc = oc["datos_cli"]
                
                st.success(f"🎉 ¡Orden #{oc['num_orden']} lista, {dc['nombres']}! Con esta compra sumas **{oc['puntos']} puntos** en el Club de Fidelidad.")
                
                with st.container(border=True):
                    st.markdown(f"### 📋 Resumen Oficial de tu Pedido (#{oc['num_orden']})")
                    st.write(f"**Cliente:** {dc['nombres']} {dc['apellidos']} | **C.I.:** {dc['cedula']}")
                    st.write(f"**Celular:** {dc['celular']}")
                    st.write(f"**Destino:** Ecuador - {dc['provincia']} - {dc['canton']}")
                    st.write(f"**Dirección Exacta:** {dc['direccion']}")
                    st.write(f"**Courier:** {dc['courier']}")
                    st.write(f"**Método de Pago:** {dc['metodo_pago']}")
                    st.markdown("---")
                    
                    for l_prod in oc["lineas_productos"]:
                        st.write(l_prod)
                    
                    st.markdown("---")
                    st.write(f"**Subtotal Calzado ({oc['total_pares']} pares):** ${oc['subtotal']:.2f}")
                    st.write(f"**Costo de Envío ({dc['canton']}):** ${oc['envio']:.2f}")
                    if oc["recargo_pp"] > 0:
                        st.write(f"**Comisión Tarjeta PayPhone (6%):** ${oc['recargo_pp']:.2f}")
                    st.markdown(f"### 💰 Total a Pagar: **${oc['total']:.2f}**")
                    
                    st.download_button(
                        label=f"📄 1. Descargar Nota de Pedido en PDF (Orden #{oc['num_orden']})",
                        data=oc["pdf_bytes"],
                        file_name=f"Pedido_{oc['num_orden']}_{dc['nombres']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="btn_descargar_pdf_fijo"
                    )
                    
                    detalle_wa_str = "\n".join(oc["lineas_productos"])
                    linea_recargo_wa = f"*Comisión PayPhone (6%):* ${oc['recargo_pp']:.2f}\n" if oc["recargo_pp"] > 0 else ""
                    
                    mensaje_wa = (
                        f"¡Hola *Mary's Store Ec / Babayork Urban*! 👠👟\n"
                        f"Envío mi Orden de Pedido *#{oc['num_orden']}* generada en la web:\n\n"
                        f"*DATOS DEL CLIENTE (FIDELIDAD):*\n"
                        f"• *Nombre:* {dc['nombres']} {dc['apellidos']}\n"
                        f"• *Cédula:* {dc['cedula']}\n"
                        f"• *Celular:* {dc['celular']}\n"
                        f"• *Ubicación:* Ecuador - {dc['provincia']} - {dc['canton']}\n"
                        f"• *Dirección:* {dc['direccion']}\n"
                        f"• *Courier:* {dc['courier']}\n"
                        f"• *Pago elegido:* {dc['metodo_pago']}\n\n"
                        f"*DETALLE DEL PEDIDO:*\n{detalle_wa_str}\n\n"
                        f"*Subtotal:* ${oc['subtotal']:.2f}\n"
                        f"*Envío:* ${oc['envio']:.2f}\n"
                        f"{linea_recargo_wa}"
                        f"*TOTAL A PAGAR: ${oc['total']:.2f}*\n\n"
                        f"Adjunto mi Nota de Pedido en PDF y quedo atento/a para finalizar el pago."
                    )
                    
                    url_wa = f"https://wa.me/593959276539?text={urllib.parse.quote(mensaje_wa)}"
                    
                    st.markdown(
                        f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">'
                        f'📲 2. Enviar Pedido a WhatsApp (0959276539) y Adjuntar PDF'
                        f'</a>',
                        unsafe_allow_html=True
                    )
                    
                    if "PayPhone" in dc["metodo_pago"]:
                        st.markdown("---")
                        st.markdown("#### 💳 Módulo de Pago con Tarjeta de Crédito / Débito (PayPhone)")
                        mensaje_pp = (
                            f"¡Hola *Mary's Store Ec / Babayork Urban*! 💳\n"
                            f"Solicito el *Link de Pago PayPhone* por el valor total de *${oc['total']:.2f}* (incluye 6% comisión pasarela) correspondiente a mi Orden *#{oc['num_orden']}*:\n\n"
                            f"• *Cliente:* {dc['nombres']} {dc['apellidos']} (C.I.: {dc['cedula']})\n"
                            f"• *Destino:* {dc['provincia']} - {dc['canton']} ({dc['direccion']})\n"
                            f"• *Detalle de artículos:*\n{detalle_wa_str}\n\n"
                            f"Quedo atento/a al enlace de PayPhone para realizar el pago."
                        )
                        url_pp = f"https://wa.me/593959276539?text={urllib.parse.quote(mensaje_pp)}"
                        st.markdown(
                            f'<a href="{url_pp}" target="_blank" class="card-btn">'
                            f'💳 Solicitar Link PayPhone por ${oc["total"]:.2f} (Con Detalle del Pedido)'
                            f'</a>',
                            unsafe_allow_html=True
                        )

# ==============================================================================
# VISTA 4: MI CUENTA (INICIO DE SESIÓN, HISTORIAL Y PUNTOS DE FIDELIDAD)
# ==============================================================================
elif st.session_state.vista_actual == "LOGIN":
    st.markdown('<div class="category-banner-black">MI CUENTA, HISTORIAL DE PEDIDOS Y FIDELIDAD</div>', unsafe_allow_html=True)
    
    if st.session_state.usuario_logueado is not None:
        u = st.session_state.usuario_logueado
        st.success(f"👋 ¡Bienvenido/a de nuevo, **{u['nombres']}**! (Cédula: {u['cedula']})")
        
        c_p1, c_p2 = st.columns([1, 2], gap="large")
        with c_p1:
            with st.container(border=True):
                st.subheader("⭐ Tu Club de Fidelidad")
                st.metric("Puntos Acumulados", f"{u['puntos']} Puntos")
                st.metric("Pares Comprados", f"{u['pares']} Pares")
                st.info("🎁 **Meta 50 Puntos (5 pares):** Ganas un **Envío Gratis** o acceso a **Promoción 2x1** coordinando directamente por nuestro WhatsApp 0959276539.")
                if st.button("🔒 Cerrar Sesión", use_container_width=True):
                    st.session_state.usuario_logueado = None
                    st.rerun()
        with c_p2:
            with st.container(border=True):
                st.subheader("📦 Mi Historial de Pedidos")
                if not df_ped.empty and "Cédula Cliente" in df_ped.columns:
                    mis_pedidos = df_ped[df_ped["Cédula Cliente"].astype(str).str.strip() == str(u["cedula"]).strip()]
                    if not mis_pedidos.empty:
                        st.dataframe(mis_pedidos, use_container_width=True)
                    else:
                        st.info("Aún no tienes pedidos registrados con tu cédula en el historial.")
                else:
                    st.info("Tus pedidos confirmados aparecerán en esta tabla.")
    else:
        col_log, col_reg = st.columns(2, gap="large")
        with col_log:
            with st.container(border=True):
                st.subheader("🔑 Iniciar Sesión")
                with st.form("form_login_cliente"):
                    ced_l = st.text_input("🪪 Número de Cédula *")
                    cor_l = st.text_input("📧 Correo Electrónico *")
                    pas_l = st.text_input("🔒 Contraseña *", type="password")
                    btn_ingresar = st.form_submit_button("Ingresar a Mi Cuenta", type="primary", use_container_width=True)
                if btn_ingresar:
                    if not ced_l:
                        st.error("Ingresa tu número de cédula.")
                    elif not df_cli.empty and "Cédula" in df_cli.columns:
                        m_cli = df_cli[df_cli["Cédula"].astype(str).str.strip() == str(ced_l).strip()]
                        if not m_cli.empty:
                            fila_u = m_cli.iloc[0]
                            st.session_state.usuario_logueado = {
                                "cedula": str(ced_l).strip(),
                                "nombres": str(fila_u.get("Nombres y Apellidos", "Cliente VIP")),
                                "puntos": limpiar_numero_int(fila_u.get("Puntos Fidelidad", 0), 0),
                                "pares": limpiar_numero_int(fila_u.get("Pares Acumulados", 0), 0)
                            }
                            st.rerun()
                        else:
                            st.warning("No encontramos esa cédula en el Club de Fidelidad. Crea tu cuenta a la derecha.")
                    else:
                        st.error("No se pudo conectar con la pestaña Fidelidad_Clientes.")

        with col_reg:
            with st.container(border=True):
                st.subheader("📝 Crear Cuenta en el Club de Fidelidad")
                with st.form("form_registro_cliente"):
                    ced_r = st.text_input("🪪 Número de Cédula (ID Único) *")
                    nom_r = st.text_input("👤 Nombres y Apellidos *")
                    cel_r = st.text_input("📱 Celular (WhatsApp) *")
                    cor_r = st.text_input("📧 Correo Electrónico *")
                    pas_r = st.text_input("🔒 Crear Contraseña *", type="password")
                    acepta_datos = st.checkbox("✅ Acepto el uso y tratamiento de mis datos personales para la gestión de pedidos y el Programa de Fidelidad de Mary's Store Ec & Babayork Urban.")
                    btn_reg = st.form_submit_button("Crear mi Cuenta", type="primary", use_container_width=True)
                if btn_reg:
                    if not (ced_r and nom_r and cel_r and cor_r and pas_r):
                        st.error("⚠️ Completa todos los campos obligatorios.")
                    elif not acepta_datos:
                        st.error("⚠️ Debes aceptar el uso y manejo de datos personales para crear tu cuenta.")
                    else:
                        st.session_state.usuario_logueado = {
                            "cedula": str(ced_r).strip(),
                            "nombres": str(nom_r).strip(),
                            "puntos": 0,
                            "pares": 0
                        }
                        st.success("🎉 ¡Cuenta creada con éxito! Ya has iniciado sesión.")
                        st.rerun()

# ==============================================================================
# VISTA 5: INFORMACIÓN DE PAGOS, ENVÍOS Y PROGRAMA DE FIDELIDAD
# ==============================================================================
elif st.session_state.vista_actual == "INFO":
    st.markdown('<div class="category-banner-black">INFORMACIÓN DE PAGOS, ENVÍOS Y FIDELIDAD</div>', unsafe_allow_html=True)
    
    ic1, ic2 = st.columns(2, gap="large")
    with ic1:
        with st.container(border=True):
            st.subheader("💳 Cómo Funcionan Nuestros Pagos")
            st.markdown("""
            1. **Transferencia o Depósito Bancario (Sin Recargo):**
               Al confirmar tu pedido en el carrito, descargas tu Nota de Pedido en PDF y la envías con un clic a nuestro WhatsApp (**0959276539**). Te compartiremos los datos bancarios oficiales para tu depósito o transferencia.
            2. **Tarjeta de Crédito o Débito vía PayPhone:**
               Aceptamos tarjetas Visa y Mastercard a través de **PayPhone**. De acuerdo con las políticas de PayPhone, los cobros con tarjeta aplican una comisión de pasarela del **5% + IVA (6% total)**, valor que se detalla automáticamente en cada producto y en tu carrito.
            3. **Pago Contraentrega (Exclusivo en Babahoyo):**
               Si te encuentras en **Babahoyo**, el envío es gratuito y pagas en efectivo al recibir tu calzado.
            """)
    with ic2:
        with st.container(border=True):
            st.subheader("⭐ Programa de Fidelidad (Cédula Única)")
            st.markdown("""
            **¿Por qué es importante registrar tus datos y tu Cédula al comprar?**
            - Tu **Número de Cédula** es tu identificador único en nuestro sistema.
            - Por cada par de calzado que compras, acumulas **10 Puntos de Fidelidad**.
            - Al alcanzar **50 puntos (5 pares acumulados)**, desbloqueas una recompensa especial a tu elección:
              - 🚚 **Un Envío Nacional 100% GRATIS**, o
              - 👠 **Promoción especial 2x1** en modelos seleccionados de temporada.
            
            ⚠️ **Importante:** El canje de puntos por envío gratis o 2x1 se realiza **únicamente en coordinación directa vía WhatsApp (0959276539)** con la tienda al momento de validar tu pedido.
            """)
