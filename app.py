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

# Estilos CSS inspirados en el diseño limpio de Deprati (Retail Moderno)
st.markdown("""
<style>
    /* Reducir márgenes superiores de Streamlit */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }
    /* Barra superior informativa */
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
    /* Cintillo negro de categoría estilo Deprati */
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
    /* Migas de pan (Breadcrumbs) */
    .breadcrumbs {
        font-size: 0.8rem;
        color: #9ca3af;
        text-transform: uppercase;
        margin-bottom: 18px;
        letter-spacing: 0.5px;
    }
    /* Tarjeta de producto e imagen con etiquetas flotantes */
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

# Funciones seguras para limpiar números y evitar ValueError ($19,99 -> 19.99)
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

# Convertidor automático de enlaces de Google Drive para que siempre carguen las fotos
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
def generar_pdf_pedido(num_orden, cliente_info, carrito, total_pares, subtotal, envio, total):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "MARY'S STORE EC & BABAYORK URBAN", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Tienda Oficial de Calzado | WhatsApp: 0959276539", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"NOTA DE PEDIDO: #{num_orden}  |  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    def limpiar_texto(txt):
        return str(txt).encode("latin-1", "replace").decode("latin-1")

    pdf.cell(0, 6, limpiar_texto(f"Cliente: {cliente_info['nombres']} {cliente_info['apellidos']} (C.I.: {cliente_info['cedula']})"), ln=True)
    pdf.cell(0, 6, limpiar_texto(f"Celular: {cliente_info['celular']}"), ln=True)
    pdf.cell(0, 6, limpiar_texto(f"Direccion / Destino: {cliente_info['direccion']}"), ln=True)
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
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(150, 9, "TOTAL A PAGAR:", 0, 0, "R")
    pdf.cell(40, 9, f"${total:.2f}", 0, 1, "R")
    
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, limpiar_texto("Importante: Este documento respalda el detalle de tu pedido. El despacho se realiza una vez confirmado el comprobante de pago por transferencia o tarjeta en nuestro WhatsApp 0959276539."))
    
    return bytes(pdf.output())

# Conexión en vivo con tu Google Sheet
SHEET_ID = "1LGRa-BfRkiRbyqukW0aWWpHJh2tKV_W-IgB0SRbx8N0"
SHEET_NAME = "Inventario"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=15)
def cargar_inventario():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        if "Modelo" in df.columns and "Color" in df.columns:
            return df
    except Exception:
        pass
    
    respaldo = [
        {"ID_Variante": 1, "Modelo": "Edilma", "Categoría": "Baletas", "Material": "Cuero - Gamusa", "Color": "Beige", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 14.50, "Mínimo Mayorista": 6, "Talla 34": 2, "Talla 35": 3, "Talla 36": 5, "Talla 37": 4, "Talla 38": 3, "Talla 39": 2, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"},
        {"ID_Variante": 2, "Modelo": "Edilma", "Categoría": "Baletas", "Material": "Cuero - Gamusa", "Color": "Rojo", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 14.50, "Mínimo Mayorista": 6, "Talla 34": 0, "Talla 35": 2, "Talla 36": 4, "Talla 37": 3, "Talla 38": 2, "Talla 39": 0, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111"},
        {"ID_Variante": 3, "Modelo": "Edilma", "Categoría": "Baletas", "Material": "Cuero - Gamusa", "Color": "Negro", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 14.50, "Mínimo Mayorista": 6, "Talla 34": 3, "Talla 35": 4, "Talla 36": 6, "Talla 37": 5, "Talla 38": 4, "Talla 39": 3, "Talla 40": 2, "Enlace Imagen": "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95"},
        {"ID_Variante": 4, "Modelo": "Flats Cadena", "Categoría": "Baletas", "Material": "Cuero", "Color": "Negro", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 15.00, "Mínimo Mayorista": 6, "Talla 34": 2, "Talla 35": 3, "Talla 36": 4, "Talla 37": 4, "Talla 38": 3, "Talla 39": 2, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a"},
        {"ID_Variante": 5, "Modelo": "Flats Cadena", "Categoría": "Baletas", "Material": "Cuero", "Color": "Palo Rosa", "Precio Regular ($)": 24.99, "Precio Oferta ($)": 19.99, "Precio Mayorista ($)": 15.00, "Mínimo Mayorista": 6, "Talla 34": 1, "Talla 35": 2, "Talla 36": 2, "Talla 37": 3, "Talla 38": 1, "Talla 39": 0, "Talla 40": 0, "Enlace Imagen": "https://images.unsplash.com/photo-1549298916-b41d501d3772"},
        {"ID_Variante": 6, "Modelo": "Sandalias Ortopédicas", "Categoría": "Sandalias", "Material": "Cuero Confort", "Color": "Blanco", "Precio Regular ($)": 32.00, "Precio Oferta ($)": 27.99, "Precio Mayorista ($)": 20.00, "Mínimo Mayorista": 6, "Talla 34": 2, "Talla 35": 3, "Talla 36": 5, "Talla 37": 5, "Talla 38": 4, "Talla 39": 2, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1608256246200-53e635b5b65f"},
        {"ID_Variante": 7, "Modelo": "Response 2", "Categoría": "Deportivos", "Material": "Sintético Transpirable", "Color": "Negro/Blanco", "Precio Regular ($)": 45.00, "Precio Oferta ($)": 39.99, "Precio Mayorista ($)": 29.99, "Mínimo Mayorista": 6, "Talla 34": 0, "Talla 35": 0, "Talla 36": 4, "Talla 37": 5, "Talla 38": 6, "Talla 39": 5, "Talla 40": 4, "Enlace Imagen": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"},
        {"ID_Variante": 8, "Modelo": "Metcon Presto", "Categoría": "Deportivos", "Material": "Malla / Sintético", "Color": "Gris/Blanco", "Precio Regular ($)": 49.99, "Precio Oferta ($)": 44.99, "Precio Mayorista ($)": 33.00, "Mínimo Mayorista": 6, "Talla 34": 0, "Talla 35": 0, "Talla 36": 3, "Talla 37": 4, "Talla 38": 5, "Talla 39": 4, "Talla 40": 3, "Enlace Imagen": "https://images.unsplash.com/photo-1608231387042-66d1773070a5"}
    ]
    return pd.DataFrame(respaldo)

df_inv = cargar_inventario()
total_items_carrito = sum(item["cantidad"] for item in st.session_state.carrito)

# ==============================================================================
# 1. CABECERA ESTILO DEPRATI (BARRA SUPERIOR + LOGOS IZQUIERDA + BUSCADOR CENTRO + CARRITO DERECHA)
# ==============================================================================
st.markdown("""
<div class="top-utility-bar">
    <span>🚚 ENVÍOS A TODO EL ECUADOR ($5 SERVIENTREGA / BUS)</span>
    <span>|</span>
    <span>📍 PAGO CONTRAENTREGA EN BABAHOYO</span>
    <span>|</span>
    <span class="top-utility-highlight">⭐ CLUB DE FIDELIDAD & MAYORISTAS: 0959276539</span>
</div>
""", unsafe_allow_html=True)

h_col_logos, h_col_search, h_col_actions = st.columns([2.2, 4.3, 2.5], vertical_alignment="center")

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
    ac1, ac2 = st.columns(2)
    with ac1:
        if st.button("📦 Mayoristas", use_container_width=True, type="secondary" if st.session_state.vista_actual != "MAYORISTA" else "primary"):
            st.session_state.vista_actual = "MAYORISTA"
            st.rerun()
    with ac2:
        if st.button(f"🛍️ Mi Carrito ({total_items_carrito})", use_container_width=True, type="primary"):
            st.session_state.vista_actual = "CARRITO"
            st.rerun()

# ==============================================================================
# 2. MENÚ HORIZONTAL DE CATEGORÍAS (ESTILO DEPRATI)
# ==============================================================================
st.markdown("<hr style='margin: 8px 0; border-color: #e5e7eb;'>", unsafe_allow_html=True)

categorias_base = sorted([str(c).strip() for c in df_inv["Categoría"].dropna().unique() if str(c).strip()])
opciones_menu = ["TODAS"] + [c.upper() for c in categorias_base] + ["🔥 REBAJAS / MAYORISTA", "🛒 IR A PAGAR"]

cols_nav = st.columns(len(opciones_menu))
for i, opcion in enumerate(opciones_menu):
    with cols_nav[i]:
        es_activo = (
            (opcion == "🛒 IR A PAGAR" and st.session_state.vista_actual == "CARRITO") or
            (opcion == "🔥 REBAJAS / MAYORISTA" and st.session_state.vista_actual == "MAYORISTA") or
            (st.session_state.vista_actual == "DETAL" and st.session_state.cat_menu == opcion)
        )
        if st.button(opcion, key=f"nav_btn_{i}", use_container_width=True, type="primary" if es_activo else "secondary"):
            if opcion == "🛒 IR A PAGAR":
                st.session_state.vista_actual = "CARRITO"
            elif opcion == "🔥 REBAJAS / MAYORISTA":
                st.session_state.vista_actual = "MAYORISTA"
                st.session_state.cat_menu = "TODAS"
            else:
                st.session_state.vista_actual = "DETAL"
                st.session_state.cat_menu = opcion
            st.rerun()

# ==============================================================================
# VISTA DE CATÁLOGO (COLUMNA IZQUIERDA DE FILTROS + GRILLA DE 3 PRODUCTOS)
# ==============================================================================
if st.session_state.vista_actual in ["DETAL", "MAYORISTA"]:
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
        solo_descuentos = st.checkbox("Solo ofertas / descuentos", value=True)

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
            st.warning("No se encontraron zapatos con esos filtros. Intenta cambiar la categoría o limpiar la búsqueda.")
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
                        
                        if p_reg > p_ofe and p_reg > 0:
                            porcentaje_desc = int(round(((p_reg - p_ofe) / p_reg) * 100))
                        else:
                            porcentaje_desc = 20
                            
                        url_limpia = preparar_url_imagen(fila_color.get("Enlace Imagen"))
                        
                        foto_placeholder.markdown(f"""
                        <div class="product-img-wrapper">
                            <span class="badge-discount">-{porcentaje_desc}%</span>
                            <span class="badge-new">NUEVO</span>
                            <img src="{url_limpia}" alt="{nombre_modelo}">
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if es_mayorista:
                            st.markdown(f"<span class='price-offer'>${p_may:.2f}</span> <span class='price-regular'>${p_ofe:.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"<div class='price-wholesale'>📦 Mayorista desde {min_may} pares</div>", unsafe_allow_html=True)
                            precio_aplicado = p_may
                        else:
                            st.markdown(f"<span class='price-offer'>${p_ofe:.2f}</span> <span class='price-regular'>${p_reg:.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"<div class='price-wholesale'>💡 Mayorista: ${p_may:.2f} ({min_may}+ pares)</div>", unsafe_allow_html=True)
                            precio_aplicado = p_ofe

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
                                        "precio_ofe": float(p_ofe),
                                        "precio_may": float(p_may),
                                        "min_may": int(min_may),
                                        "subtotal": round(int(cantidad_pedir) * float(precio_aplicado), 2),
                                        "imagen": url_limpia
                                    })
                                    st.toast(f"✅ {nombre_modelo} ({color_elegido} - Talla {talla_elegida}) agregado al carrito.")
                                    st.rerun()
                        else:
                            st.markdown("<div class='stock-zero'>❌ Agotado en este color y talla (0)</div>", unsafe_allow_html=True)
                            st.caption("Elige otro color u otra talla.")
                            
                tarjeta_idx += 1

# ==============================================================================
# VISTA 3: VENTANA DEL CARRITO, DATOS DE CLIENTE (FIDELIDAD), PDF Y PAGO
# ==============================================================================
elif st.session_state.vista_actual == "CARRITO":
    st.markdown('<div class="category-banner-black">MI CARRITO Y FINALIZACIÓN DE COMPRA</div>', unsafe_allow_html=True)
    
    if st.button("⬅️ Seguir Comprando en el Catálogo"):
        st.session_state.vista_actual = "DETAL"
        st.rerun()
        
    if len(st.session_state.carrito) == 0:
        st.info("Tu carrito está vacío actualmente. Explora nuestro catálogo, elige color y talla y agrégalos a tu bolsa.")
    else:
        col_resumen, col_checkout = st.columns([1.15, 1.25], gap="large")
        
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
                    etiqueta_precio = "Precio Oferta Detal"
                
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
                            st.rerun()
            
            if st.button("🧹 Vaciar todo el carrito"):
                st.session_state.carrito = []
                st.rerun()

        with col_checkout:
            st.subheader("2. Datos de Envío y Club de Fidelidad")
            st.caption("Completa tus datos para generar tu Nota de Pedido en PDF y coordinar tu entrega.")
            
            with st.form("form_checkout"):
                cedula = st.text_input("🪪 Número de Cédula / RUC *")
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    nombres = st.text_input("👤 Nombres *")
                with col_n2:
                    apellidos = st.text_input("👤 Apellidos *")
                
                celular = st.text_input("📱 Número de Celular (WhatsApp) *")
                direccion = st.text_area("📍 Dirección exacta y Ciudad de destino *")
                
                courier = st.selectbox(
                    "🚚 Método de Envío / Courier Preferido *",
                    [
                        "Servientrega a domicilio / agencia (+$5.00)",
                        "Encargo en Cooperativa de Bus Interprovincial (+$5.00)",
                        "Pago Contraentrega (Exclusivo dentro de Babahoyo - $0.00)"
                    ]
                )
                
                metodo_pago = st.radio(
                    "💳 Selecciona cómo deseas pagar:",
                    [
                        "Transferencia / Depósito Bancario (Coordinar por WhatsApp)",
                        "Pago en Línea con Tarjeta de Crédito / Débito (PayPhone)",
                        "Efectivo Contraentrega (Solo Babahoyo)"
                    ]
                )
                
                confirmar_btn = st.form_submit_button("✅ Confirmar Pedido y Generar PDF", type="primary", use_container_width=True)

            if confirmar_btn:
                if not (cedula and nombres and apellidos and celular and direccion):
                    st.error("⚠️ Por favor completa todos los campos obligatorios (*) para continuar.")
                else:
                    costo_envio = 0.0 if "Babahoyo" in courier else 5.00
                    total_pagar = round(subtotal_general + costo_envio, 2)
                    puntos_ganados = int(total_pares_carrito * 10)
                    num_orden = f"MB-{random.randint(1000, 9999)}"
                    
                    st.success(f"🎉 ¡Orden #{num_orden} lista, {nombres}! Con esta compra sumas **{puntos_ganados} puntos** en el Club de Fidelidad.")
                    
                    with st.container(border=True):
                        st.markdown(f"### 📋 Resumen Oficial de tu Pedido (#{num_orden})")
                        st.write(f"**Cliente:** {nombres} {apellidos} | **C.I.:** {cedula}")
                        st.write(f"**Celular:** {celular}")
                        st.write(f"**Dirección de Entrega:** {direccion}")
                        st.write(f"**Courier:** {courier}")
                        st.write(f"**Método de Pago:** {metodo_pago}")
                        st.markdown("---")
                        
                        lineas_productos = []
                        for item in st.session_state.carrito:
                            p_u = item["precio_may"] if total_pares_carrito >= item["min_may"] else item["precio_ofe"]
                            sub_i = round(p_u * item["cantidad"], 2)
                            linea_txt = f"- {item['cantidad']}x {item['modelo']} (Color: {item['color']} | Talla: {item['talla']}) = ${sub_i:.2f}"
                            st.write(linea_txt)
                            lineas_productos.append(linea_txt)
                        
                        st.markdown("---")
                        st.write(f"**Subtotal Calzado ({total_pares_carrito} pares):** ${subtotal_general:.2f}")
                        st.write(f"**Costo de Envío:** ${costo_envio:.2f}")
                        st.markdown(f"### 💰 Total a Pagar: **${total_pagar:.2f}**")
                        
                        datos_cli = {
                            "cedula": cedula, "nombres": nombres, "apellidos": apellidos,
                            "celular": celular, "direccion": direccion, "courier": courier, "metodo_pago": metodo_pago
                        }
                        pdf_bytes = generar_pdf_pedido(num_orden, datos_cli, st.session_state.carrito, total_pares_carrito, subtotal_general, costo_envio, total_pagar)

                        st.download_button(
                            label=f"📄 1. Descargar Nota de Pedido en PDF (Orden #{num_orden})",
                            data=pdf_bytes,
                            file_name=f"Pedido_{num_orden}_{nombres}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        mensaje_wa = (
                            f"¡Hola *Mary's Store Ec / Babayork Urban*! 👠👟\n"
                            f"Envío mi Orden de Pedido *#{num_orden}* generada en la web:\n\n"
                            f"*DATOS DEL CLIENTE (FIDELIDAD):*\n"
                            f"• *Nombre:* {nombres} {apellidos}\n"
                            f"• *Cédula:* {cedula}\n"
                            f"• *Celular:* {celular}\n"
                            f"• *Dirección:* {direccion}\n"
                            f"• *Courier:* {courier}\n"
                            f"• *Pago elegido:* {metodo_pago}\n\n"
                            f"*DETALLE DEL PEDIDO:*\n" +
                            "\n".join(lineas_productos) +
                            f"\n\n*Subtotal:* ${subtotal_general:.2f}\n"
                            f"*Envío:* ${costo_envio:.2f}\n"
                            f"*TOTAL A PAGAR: ${total_pagar:.2f}*\n\n"
                            f"Adjunto mi Nota de Pedido en PDF y quedo atento/a para finalizar el pago."
                        )
                        
                        url_wa = f"https://wa.me/593959276539?text={urllib.parse.quote(mensaje_wa)}"
                        
                        st.markdown(
                            f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">'
                            f'📲 2. Enviar Pedido a WhatsApp (0959276539) y Adjuntar PDF'
                            f'</a>',
                            unsafe_allow_html=True
                        )
                        
                        if "Tarjeta" in metodo_pago:
                            st.markdown("---")
                            st.markdown("#### 💳 Módulo de Pago con Tarjeta de Crédito / Débito (PayPhone)")
                            st.info(
                                "Para pagos inmediatos con tarjeta Visa o Mastercard en Ecuador, "
                                "haz clic en el botón de abajo para solicitar tu Link de Cobro PayPhone por el valor exacto de tu orden."
                            )
                            LINK_PASARELA_TARJETA = "https://wa.me/593959276539?text=" + urllib.parse.quote(
                                f"Hola, solicito el Link de Pago con Tarjeta (PayPhone) por el valor de ${total_pagar:.2f} correspondiente a mi Orden #{num_orden} a nombre de {nombres} {apellidos}."
                            )
                            st.markdown(
                                f'<a href="{LINK_PASARELA_TARJETA}" target="_blank" class="card-btn">'
                                f'💳 Solicitar Link PayPhone por ${total_pagar:.2f}'
                                f'</a>',
                                unsafe_allow_html=True
                            )
