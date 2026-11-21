import streamlit as st
import pandas as pd
import urllib.parse
import re
import os
import random
from datetime import datetime, timezone, timedelta

# Zona horaria oficial de Ecuador (America/Guayaquil, UTC-5)
ECUADOR_TZ = timezone(timedelta(hours=-5))

def ahora_ecuador():
    return datetime.now(ECUADOR_TZ)
from fpdf import FPDF
import urllib.request
import json
import base64
import io
import tempfile

# URL de tu Google Apps Script conectada directamente
GOOGLE_SCRIPT_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxC43z42rdBydVWuyihHfr4qR8AyZ4_mIaD3sYyAGdh67-dAVc6LUGu6vzgIZHIf57Ldg/exec"

# Enlaces Oficiales de Redes Sociales
URL_FACEBOOK = "https://www.facebook.com/share/1CN5wrLMTH/?mibextid=wwXIfr"
URL_INSTAGRAM = "https://www.instagram.com/ec_marystore?dmpr=dDJiaWw4MDRybGRt&utm_source=qr"
WHATSAPP_NUMERO = "593959276539"

def obtener_ruta_logo():
    candidatos = [
        ("logo_marys_horizontal.png", "image/png"),
        ("logo_marys_horizontal.jpg", "image/jpeg"),
        ("logo_marys_horizontal.jpeg", "image/jpeg"),
        ("logo_marys_ec.png", "image/png"),
        ("logo_marys_ec.jpg", "image/jpeg"),
        ("logo_marys_ec.jpeg", "image/jpeg"),
    ]
    for ruta, mime in candidatos:
        if os.path.exists(ruta):
            return ruta, mime
    return None, None

def obtener_ruta_logo_pdf():
    candidatos_pdf = [
        "logo_marys_vertical (Sin fondo).png",
        "logo_marys_vertical.png",
        "logo_marys_vertical.jpg",
        "logo_marys_horizontal.png",
        "logo_marys_horizontal.jpg",
        "logo_marys_ec.png",
    ]
    for ruta in candidatos_pdf:
        if os.path.exists(ruta):
            return ruta
    return None

def obtener_logo_base64():
    ruta, mime = obtener_ruta_logo()
    if ruta:
        with open(ruta, "rb") as img_f:
            return mime, base64.b64encode(img_f.read()).decode("utf-8")
    return None, None

def enviar_a_google_sheet(payload):
    if not GOOGLE_SCRIPT_WEBHOOK_URL:
        return False
    try:
        req = urllib.request.Request(
            GOOGLE_SCRIPT_WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.status == 200
    except Exception:
        return False

# Configuración general de la tienda
st.set_page_config(
    page_title="Mary's Store EC | Tienda Online Oficial",
    page_icon="👠",
    layout="wide"
)

# Estilos CSS: Layout estilo Deprati + Identidad de Marca @marys_store_ec
# Paleta: Marfil suave (#FAF7F2), Negro charol (#1A1A1A), Caramelo (#C49A6C), Vino boutique (#9E1B32)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    .stApp {
        background-color: #FAF7F2;
    }
    .block-container {
        padding-top: 3.4rem !important;
        padding-bottom: 1.5rem !important;
    }
    .top-utility-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        font-size: 0.75rem;
        color: #4b5563;
        border-bottom: 1px solid #E5DFD5;
        padding-bottom: 8px;
        margin-bottom: 14px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .top-utility-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .top-utility-right {
        display: flex;
        align-items: center;
        gap: 14px;
        flex-wrap: wrap;
    }
    .social-subtle {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        color: #1A1A1A !important;
        text-decoration: none !important;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: none;
        letter-spacing: 0.2px;
        padding: 2px 6px;
        border-radius: 4px;
        transition: color 0.2s ease, background-color 0.2s ease;
    }
    .social-subtle:hover {
        color: #9E1B32 !important;
        background-color: #EFEAE1;
    }
    .top-utility-highlight {
        color: #9E1B32;
        font-weight: 700;
    }
    /* Imagen de logotipo integrada sin recuadro y con mayor tamaño */
    .header-logo-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        overflow: hidden;
        margin: -10px 0;
    }
    .header-logo-img {
        width: 100%;
        max-width: 325px;
        height: auto;
        display: block;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
        filter: brightness(1.03) contrast(1.05);
        mix-blend-mode: multiply;
    }
    /* Logotipo Horizontal @marys_store_ec (Sello circular doble aro + tipografía editorial) */
    .brand-logo-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 2px 0;
    }
    .brand-seal {
        width: 54px;
        height: 54px;
        min-width: 54px;
        border-radius: 50%;
        border: 1.8px solid #1A1A1A;
        padding: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #FAF7F2;
        box-sizing: border-box;
    }
    .brand-seal-inner {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 1.3px solid #C49A6C;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #1A1A1A;
        letter-spacing: -1px;
    }
    .brand-text-block {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .brand-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.38rem;
        font-weight: 700;
        color: #1A1A1A;
        line-height: 1.1;
        letter-spacing: 0.3px;
    }
    .brand-divider {
        height: 1.5px;
        width: 100%;
        background-color: #C49A6C;
        margin: 4px 0 3px 0;
    }
    .brand-subtitle {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.62rem;
        font-weight: 600;
        color: #4B5563;
        letter-spacing: 3.2px;
        text-transform: uppercase;
    }
    /* Cintillo negro charol con acento caramelo */
    .category-banner-black {
        background-color: #1A1A1A;
        color: #FAF7F2;
        padding: 18px 28px;
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.6rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 8px;
        margin-bottom: 12px;
        border-bottom: 3px solid #C49A6C;
    }
    .breadcrumbs {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.78rem;
        color: #78716C;
        text-transform: uppercase;
        margin-bottom: 18px;
        letter-spacing: 0.6px;
    }
    /* Tarjetas de producto limpias sobre fondo marfil */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-color: #E7E2D8 !important;
        border-radius: 6px !important;
    }
    .product-img-wrapper {
        position: relative;
        background-color: #F5F2EC;
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
        background-color: #9E1B32;
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
        background-color: #1A1A1A;
        color: #FAF7F2;
        padding: 3px 10px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        z-index: 2;
    }
    .product-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.05rem;
        color: #1A1A1A;
        font-weight: 700;
        margin: 4px 0 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .product-sub {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.78rem;
        color: #6B7280;
        margin-bottom: 6px;
    }
    .price-offer {
        color: #9E1B32;
        font-size: 1.25rem;
        font-weight: 800;
        margin-right: 8px;
    }
    .price-regular {
        text-decoration: line-through;
        color: #9CA3AF;
        font-size: 0.92rem;
    }
    .price-wholesale {
        background-color: #FAF7F2;
        border: 1px solid #C49A6C;
        color: #7C5A34;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.76rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .stock-ok {
        color: #065F46;
        font-size: 0.8rem;
        font-weight: 700;
        background: #ECFDF5;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .stock-zero {
        color: #991B1B;
        font-size: 0.8rem;
        font-weight: 700;
        background: #FEF2F2;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .sidebar-filter-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.88rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #1A1A1A;
        border-bottom: 2px solid #C49A6C;
        padding-bottom: 6px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    .payment-box-detail {
        border: 1px solid #E5DFD5;
        border-radius: 10px;
        padding: 16px;
        background-color: #FFFFFF;
        margin: 14px 0;
        box-shadow: 0 2px 6px rgba(26, 26, 26, 0.04);
    }
    .whatsapp-btn {
        display: block;
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 14px 20px;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: bold;
        font-size: 1.05rem;
        margin-top: 12px;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.25);
    }
    .whatsapp-consult-btn {
        display: block;
        background-color: #128C7E;
        color: white !important;
        text-align: center;
        padding: 11px 16px;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 0.94rem;
        margin-top: 10px;
        margin-bottom: 12px;
        box-shadow: 0 3px 8px rgba(18, 140, 126, 0.22);
    }
    .card-btn {
        display: block;
        background-color: #1A1A1A;
        color: #FAF7F2 !important;
        text-align: center;
        padding: 14px 20px;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: bold;
        font-size: 1.05rem;
        margin-top: 10px;
        border: 1px solid #C49A6C;
    }
    .store-footer {
        margin-top: 28px;
        padding: 12px 22px;
        background-color: #1A1A1A;
        color: #D1D5DB;
        border-radius: 6px;
        border-top: 2px solid #C49A6C;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .footer-copy {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.76rem;
        color: #A8A29E;
    }
    .footer-socials {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .footer-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 4px;
        border: 1px solid rgba(196, 154, 108, 0.45);
        background-color: rgba(255, 255, 255, 0.04);
        color: #FAF7F2 !important;
        text-decoration: none !important;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }
    .footer-link:hover {
        background-color: rgba(196, 154, 108, 0.22);
        border-color: #C49A6C;
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
if "registro_autocompletado" not in st.session_state:
    st.session_state.registro_autocompletado = {}

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

def limpiar_texto_campo(valor):
    if valor is None or pd.isna(valor):
        return ""
    s = str(valor).strip()
    if s.lower() in ("nan", "none"):
        return ""
    if s.startswith("'"):
        s = s[1:]
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    return s

def normalizar_id(valor):
    s = limpiar_texto_campo(valor)
    if not s:
        return ""
    solo_digitos = "".join(ch for ch in s if ch.isdigit())
    if len(solo_digitos) == 9:
        solo_digitos = "0" + solo_digitos
    return solo_digitos if solo_digitos else s

def agregar_al_carrito(nuevo_item, stock_max=None):
    mod_n = str(nuevo_item.get("modelo", "")).strip().lower()
    col_n = str(nuevo_item.get("color", "")).strip().lower()
    tal_n = str(nuevo_item.get("talla", "")).strip().lower()

    for existente in st.session_state.carrito:
        if (
            str(existente.get("modelo", "")).strip().lower() == mod_n
            and str(existente.get("color", "")).strip().lower() == col_n
            and str(existente.get("talla", "")).strip().lower() == tal_n
        ):
            nueva_cant = int(existente["cantidad"]) + int(nuevo_item["cantidad"])
            if stock_max is not None and nueva_cant > int(stock_max):
                nueva_cant = int(stock_max)
            existente["cantidad"] = nueva_cant
            existente["subtotal"] = round(nueva_cant * float(existente["precio_unitario"]), 2)
            return True, nueva_cant

    st.session_state.carrito.append(nuevo_item)
    return False, int(nuevo_item["cantidad"])

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

def formatear_codigo_producto(id_valor):
    s = limpiar_texto_campo(id_valor)
    if not s:
        return "MS-000"
    if s.upper().startswith("MS-"):
        return s.upper()
    if s.isdigit():
        return f"MS-{int(s):03d}"
    return f"MS-00{s}"

def descargar_imagen_para_pdf(url_o_ruta):
    if not url_o_ruta:
        return None
    try:
        from PIL import Image as PILImage
        if os.path.exists(str(url_o_ruta)):
            im = PILImage.open(str(url_o_ruta))
        else:
            req = urllib.request.Request(
                str(url_o_ruta),
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                raw = resp.read()
            im = PILImage.open(io.BytesIO(raw))
        im = im.convert("RGB")
        im.thumbnail((180, 180))
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        im.save(tmp.name, format="JPEG", quality=85)
        tmp.close()
        return tmp.name
    except Exception:
        return None

# Función para generar Nota de Pedido en PDF
def generar_pdf_pedido(num_orden, fecha_str, cliente_info, carrito, total_pares, subtotal, envio, recargo_pp, total):
    pdf = FPDF()
    pdf.add_page()
    
    # Insertar logotipo vertical sin fondo centrado (sin superposición de texto)
    ruta_logo_pdf = obtener_ruta_logo_pdf()
    logo_insertado = False
    if ruta_logo_pdf:
        try:
            ancho_logo = 58
            x_centrado = (210 - ancho_logo) / 2
            y_inicio = 10
            altura_logo = 48
            try:
                from PIL import Image as PILImage
                with PILImage.open(ruta_logo_pdf) as im_tmp:
                    w_px, h_px = im_tmp.size
                    if w_px > 0:
                        altura_logo = ancho_logo * (h_px / w_px)
            except Exception:
                altura_logo = 48
            pdf.image(ruta_logo_pdf, x=x_centrado, y=y_inicio, w=ancho_logo)
            pdf.set_y(y_inicio + altura_logo + 6)
            logo_insertado = True
        except Exception:
            logo_insertado = False
            
    if not logo_insertado:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "MARY'S STORE EC", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Tienda Online Oficial | WhatsApp: 0959276539", ln=True, align="C")
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
    
    # Tabla con 8 columnas (Ancho total = 190mm): Foto, Código, Modelo, Color, Talla, Cant., Precio Unit., Subtotal
    def dibujar_encabezado_tabla():
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_fill_color(235, 230, 222)
        pdf.cell(22, 8, "Foto", 1, 0, "C", True)
        pdf.cell(22, 8, "Codigo", 1, 0, "C", True)
        pdf.cell(44, 8, "Modelo", 1, 0, "L", True)
        pdf.cell(26, 8, "Color", 1, 0, "C", True)
        pdf.cell(14, 8, "Talla", 1, 0, "C", True)
        pdf.cell(14, 8, "Cant.", 1, 0, "C", True)
        pdf.cell(24, 8, "Precio Unit.", 1, 0, "R", True)
        pdf.cell(24, 8, "Subtotal", 1, 1, "R", True)

    dibujar_encabezado_tabla()
    
    row_h = 20
    pdf.set_font("Helvetica", "", 8.5)
    for item in carrito:
        if pdf.get_y() + row_h > 270:
            pdf.add_page()
            dibujar_encabezado_tabla()
            pdf.set_font("Helvetica", "", 8.5)

        p_u = item["precio_may"] if total_pares >= item["min_may"] else item["precio_ofe"]
        sub_i = round(p_u * item["cantidad"], 2)
        cod_prod = formatear_codigo_producto(item.get("codigo", item.get("id_variante", "000")))

        x_ini = pdf.get_x()
        y_ini = pdf.get_y()

        # Celda de foto
        pdf.cell(22, row_h, "", 1, 0, "C")
        ruta_img_tmp = descargar_imagen_para_pdf(item.get("imagen", ""))
        if ruta_img_tmp:
            try:
                pdf.image(ruta_img_tmp, x=x_ini + 3, y=y_ini + 2, w=16, h=16)
            except Exception:
                pass
            finally:
                try:
                    os.remove(ruta_img_tmp)
                except Exception:
                    pass

        pdf.set_xy(x_ini + 22, y_ini)
        pdf.cell(22, row_h, limpiar_texto(cod_prod)[:12], 1, 0, "C")
        pdf.cell(44, row_h, limpiar_texto(item["modelo"])[:22], 1, 0, "L")
        pdf.cell(26, row_h, limpiar_texto(item["color"])[:14], 1, 0, "C")
        pdf.cell(14, row_h, limpiar_texto(item["talla"]), 1, 0, "C")
        pdf.cell(14, row_h, str(item["cantidad"]), 1, 0, "C")
        pdf.cell(24, row_h, f"${p_u:.2f}", 1, 0, "R")
        pdf.cell(24, row_h, f"${sub_i:.2f}", 1, 1, "R")
        
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(156, 7, "Subtotal:", 0, 0, "R")
    pdf.cell(34, 7, f"${subtotal:.2f}", 0, 1, "R")
    pdf.cell(156, 7, "Costo de Envio:", 0, 0, "R")
    pdf.cell(34, 7, f"${envio:.2f}", 0, 1, "R")
    if recargo_pp > 0:
        pdf.cell(156, 7, "Comision Pasarela Tarjeta (6%):", 0, 0, "R")
        pdf.cell(34, 7, f"${recargo_pp:.2f}", 0, 1, "R")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(156, 9, "TOTAL A PAGAR:", 0, 0, "R")
    pdf.cell(34, 9, f"${total:.2f}", 0, 1, "R")
    
    if "Transferencia" in cliente_info.get("metodo_pago", ""):
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "CUENTAS BANCARIAS PARA TRANSFERENCIA / DEPOSITO:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, "Titular: Maria Jose Gonzales Arriaga | C.I.: 1205602178", ln=True)
        pdf.cell(0, 5, "- Banco Pichincha (Cta. Ahorros): 2204179577", ln=True)
        pdf.cell(0, 5, "- Banco Guayaquil (Cta. Ahorros): 22751072", ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, limpiar_texto("Importante: Este documento respalda el detalle de tu pedido en Mary's Store EC. El despacho se realiza una vez confirmado el comprobante de pago en nuestro WhatsApp 0959276539."))
    
    salida = pdf.output(dest="S")
    return bytes(salida) if isinstance(salida, (bytes, bytearray)) else salida.encode("latin-1")

# Conexión en vivo con Google Sheets
SHEET_ID = "1LGRa-BfRkiRbyqukW0aWWpHJh2tKV_W-IgB0SRbx8N0"
URL_INV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Inventario"
URL_CLI = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Fidelidad_Clientes"
URL_ENV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Costos_Envio"
URL_PED = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Ventas_Historial"

@st.cache_data(ttl=15)
def cargar_sheet(url, como_texto=False):
    try:
        if como_texto:
            df = pd.read_csv(url, dtype=str, keep_default_na=False)
        else:
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
df_cli = cargar_sheet(URL_CLI, como_texto=True)
df_ped = cargar_sheet(URL_PED, como_texto=True)

total_items_carrito = sum(item["cantidad"] for item in st.session_state.carrito)

# ==============================================================================
# 1. CABECERA MARY'S STORE EC + REDES SOCIALES DISCRETAS
# ==============================================================================
st.markdown(f"""
<div class="top-utility-bar">
    <div class="top-utility-left">
        <a href="{URL_FACEBOOK}" target="_blank" class="social-subtle"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M22.675 0h-21.35c-.732 0-1.325.593-1.325 1.325v21.351c0 .731.593 1.324 1.325 1.324h11.495v-9.294h-3.128v-3.622h3.128v-2.671c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12v9.293h6.116c.73 0 1.323-.593 1.323-1.325v-21.35c0-.732-.593-1.325-1.325-1.325z"/></svg> Facebook</a>
        <span style="color:#d1d5db;">|</span>
        <a href="{URL_INSTAGRAM}" target="_blank" class="social-subtle"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg> Instagram</a>
    </div>
    <div class="top-utility-right">
        <span>🚚 ENVÍOS A TODO EL ECUADOR</span>
        <span>|</span>
        <span class="top-utility-highlight">⭐ CLUB DE FIDELIDAD & MAYORISTAS</span>
    </div>
</div>
""", unsafe_allow_html=True)

h_col_logo, h_col_search, h_col_actions = st.columns([2.4, 3.9, 2.7], vertical_alignment="center")

with h_col_logo:
    # Muestra tu logotipo subido a GitHub integrado sin recuadro y aprovechando el espacio de la columna
    logo_mime, logo_b64 = obtener_logo_base64()
    if logo_b64:
        st.markdown(
            f'<div class="header-logo-container"><img src="data:{logo_mime};base64,{logo_b64}" class="header-logo-img" alt="Mary\'s Store EC"></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown("""
        <div class="brand-logo-wrap">
            <div class="brand-seal">
                <div class="brand-seal-inner">MS</div>
            </div>
            <div class="brand-text-block">
                <div class="brand-name">Mary's Store EC</div>
                <div class="brand-divider"></div>
                <div class="brand-subtitle">TIENDA ONLINE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
st.markdown("<hr style='margin: 8px 0; border-color: #E5DFD5;'>", unsafe_allow_html=True)

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
        
        st.markdown(f"<h2 style='margin-bottom:2px; color:#1A1A1A; font-family:Playfair Display, serif;'>{nombre_mod_sel}</h2>", unsafe_allow_html=True)
        caption_codigo_placeholder = st.empty()
        
        colores_disponibles = list(variantes_prod["Color"].dropna().unique())
        idx_col = colores_disponibles.index(color_inicial) if (color_inicial in colores_disponibles) else 0
        
        sc1, sc2 = st.columns(2)
        with sc1:
            color_sel_det = st.selectbox("🎨 COLOR *", colores_disponibles, index=idx_col, key="det_color_sel")
        with sc2:
            talla_sel_det = st.selectbox("📏 TALLA *", ["34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"], index=2, key="det_talla_sel")
            
        filas_color_det = variantes_prod[variantes_prod["Color"] == color_sel_det]
        fila_activa = filas_color_det.iloc[0] if not filas_color_det.empty else fila_base
        codigo_prod_det = formatear_codigo_producto(fila_activa.get("ID_Variante", "001"))
        caption_codigo_placeholder.caption(f"Código: **{codigo_prod_det}** | Categoría: **{cat_prod}** | Tienda: **Mary's Store EC**")
        
        p_reg_d = limpiar_numero_float(fila_activa.get("Precio Regular ($)", 24.99), 24.99)
        p_ofe_d = limpiar_numero_float(fila_activa.get("Precio Oferta ($)", 19.99), 19.99)
        p_may_d = limpiar_numero_float(fila_activa.get("Precio Mayorista ($)", p_ofe_d * 0.75), round(p_ofe_d * 0.75, 2))
        min_may_d = max(1, limpiar_numero_int(fila_activa.get("Mínimo Mayorista", 6), 6))
        en_oferta_d = str(fila_activa.get("En Oferta", "Si")).strip().lower() in ["si", "sí", "yes", "true", "1"]
        
        precio_base_det = p_ofe_d if en_oferta_d else p_reg_d
        precio_payphone_det = round(precio_base_det * 1.06, 2)
        
        st.markdown(f"""
        <div class="payment-box-detail">
            <div style="font-size:0.78rem; color:#7C5A34; font-weight:700; text-transform:uppercase; margin-bottom:8px; letter-spacing:0.6px;">
                MÉTODOS DE PAGO Y PRECIOS
            </div>
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="flex:1; padding-right:14px; border-right:2px solid #C49A6C;">
                    <div style="font-size:0.95rem; font-weight:700; color:#1A1A1A;">Transferencia / Depósito</div>
                    <div style="font-size:1.55rem; font-weight:800; color:#9E1B32;">${precio_base_det:.2f}</div>
                    <div style="font-size:0.75rem; color:#6b7280;">Sin recargo • Mayorista: ${p_may_d:.2f} ({min_may_d}+ pares)</div>
                </div>
                <div style="flex:1; padding-left:16px;">
                    <div style="font-size:0.95rem; font-weight:700; color:#1A1A1A;">Tarjeta de Crédito (PayPhone)</div>
                    <div style="font-size:1.55rem; font-weight:800; color:#1A1A1A;">${precio_payphone_det:.2f}</div>
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
                    consolidado, cant_total_item = agregar_al_carrito({
                        "codigo": codigo_prod_det,
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
                    }, stock_max=stock_det)
                    st.session_state.orden_confirmada = None
                    if consolidado:
                        st.toast(f"✅ Cantidad actualizada en tu carrito: {cant_total_item}x {nombre_mod_sel} ({color_sel_det} - Talla {talla_sel_det}).")
                    else:
                        st.toast(f"✅ {nombre_mod_sel} ({color_sel_det} - Talla {talla_sel_det}) añadido al carrito.")
                    st.rerun()
        else:
            st.markdown(f"<div class='stock-zero'>❌ Agotado en color {color_sel_det} y talla {talla_sel_det} (Stock: 0)</div>", unsafe_allow_html=True)

        # Botón directo de WhatsApp para consultas con la info del artículo pre-cargada
        msg_consulta_prod = (
            f"¡Hola *Mary's Store EC*! 👋\n"
            f"Tengo una consulta sobre este artículo de su tienda online:\n\n"
            f"• *Modelo:* {nombre_mod_sel} (Cód: {codigo_prod_det})\n"
            f"• *Categoría:* {cat_prod}\n"
            f"• *Color:* {color_sel_det}\n"
            f"• *Talla de interés:* {talla_sel_det}\n"
            f"• *Precio Transferencia:* ${precio_base_det:.2f}\n"
            f"• *Precio Tarjeta (PayPhone):* ${precio_payphone_det:.2f}\n\n"
            f"Mi consulta es: "
        )
        url_wa_consulta = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg_consulta_prod)}"
        st.markdown(
            f'<a href="{url_wa_consulta}" target="_blank" class="whatsapp-consult-btn">'
            f'💬 ¿Tienes dudas sobre este calzado? Consultar por WhatsApp'
            f'</a>',
            unsafe_allow_html=True
        )
            
        st.markdown("#### Características del Calzado:")
        st.markdown(f"""
        - **Modelo:** {nombre_mod_sel}
        - **Color seleccionado:** {color_sel_det}
        - **Material:** {mat_prod} de alta durabilidad y confort
        - **Tallas disponibles:** 34 al 44
        - **Envíos:** A todo el Ecuador por Servientrega o Cooperativa de Transporte.
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
            | **41** | 26.1 - 26.5 cm | 9.5 |
            | **42** | 26.6 - 27.0 cm | 10.0 |
            | **43** | 27.1 - 27.8 cm | 10.5 - 11.0 |
            | **44** | 27.9 - 28.5 cm | 11.5 - 12.0 |
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
# VISTA DE CATÁLOGO PRINCIPAL (LAYOUT DEPRATI + PALETA @marys_store_ec)
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
        st.info("📦 **Modo Mayorista Activo:** Precios especiales por volumen (combinando tallas y colores) directamente en Mary's Store EC.")

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
            talla_filtro = st.selectbox("Ver stock en talla:", ["Todas las tallas", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"], label_visibility="collapsed")

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
                            tallas_lista = ["34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"]
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
                                    codigo_prod_grid = formatear_codigo_producto(fila_color.get("ID_Variante", "001"))
                                    consolidado, cant_total_item = agregar_al_carrito({
                                        "codigo": codigo_prod_grid,
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
                                    }, stock_max=stock_disponible)
                                    st.session_state.orden_confirmada = None
                                    if consolidado:
                                        st.toast(f"✅ Cantidad actualizada en tu carrito: {cant_total_item}x {nombre_modelo} ({color_elegido} - Talla {talla_elegida}).")
                                    else:
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
            
            c_busq1, c_busq2 = st.columns([2.5, 1], vertical_alignment="bottom")
            with c_busq1:
                ced_buscar = st.text_input("🪪 ¿Ya has comprado antes? Ingresa tu Cédula para autocompletar tus datos:", placeholder="Ej: 1204567890")
            with c_busq2:
                if st.button("🔍 Buscar Cédula", use_container_width=True):
                    ced_norm_b = normalizar_id(ced_buscar)
                    if ced_norm_b and not df_cli.empty and "Cédula" in df_cli.columns:
                        coincidencia = df_cli[df_cli["Cédula"].apply(normalizar_id) == ced_norm_b]
                        if not coincidencia.empty:
                            fila_c = coincidencia.iloc[0]
                            nom_comp = limpiar_texto_campo(fila_c.get("Nombres y Apellidos", ""))
                            partes = nom_comp.split(" ", 1)
                            st.session_state.cliente_autocompletado = {
                                "cedula": ced_norm_b,
                                "nombres": partes[0] if len(partes) > 0 else "",
                                "apellidos": partes[1] if len(partes) > 1 else "",
                                "celular": normalizar_id(fila_c.get("Celular", "")),
                                "provincia": limpiar_texto_campo(fila_c.get("Provincia", "Los Ríos")) or "Los Ríos",
                                "canton": limpiar_texto_campo(fila_c.get("Cantón", "Babahoyo")) or "Babahoyo",
                                "direccion": limpiar_texto_campo(fila_c.get("Dirección", fila_c.get("Dirección y Ciudad", "")))
                            }
                            st.success(f"✅ ¡Datos recuperados! Puntos acumulados: {limpiar_numero_int(fila_c.get('Puntos Fidelidad', 0), 0)} pts.")
                        else:
                            st.info("Cédula nueva. Completa tus datos abajo para registrarte.")
                            st.session_state.cliente_autocompletado = {"cedula": ced_norm_b}

            ca = st.session_state.cliente_autocompletado
            
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

            # Costo de envío según Sheet Costos_Envio (tarifa configurada por Provincia/Cantón)
            costo_envio_calc = 5.00
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
                        f"Encargo en Cooperativa de Bus Interprovincial (+${costo_envio_calc:.2f})"
                    ]
                )
                
                metodo_pago = st.radio(
                    "💳 Selecciona cómo deseas pagar:",
                    [
                        "Transferencia / Depósito Bancario (Sin recargo)",
                        "Pago en Línea con Tarjeta de Crédito / Débito - PayPhone (+6% comisión pasarela)"
                    ]
                )
                
                guardar_fidelidad = st.checkbox("⭐ Deseo guardar mis datos para futuras compras y acumular puntos en el Club de Fidelidad", value=True)
                
                confirmar_btn = st.form_submit_button("✅ Confirmar Datos y Generar Orden de Compra", type="primary", use_container_width=True)

            if confirmar_btn:
                if not (cedula and nombres and apellidos and celular and direccion):
                    st.error("⚠️ Por favor completa todos los campos obligatorios (*) para continuar.")
                else:
                    envio_final = costo_envio_calc
                    recargo_payphone = round(subtotal_general * 0.06, 2) if "PayPhone" in metodo_pago else 0.0
                    total_pagar = round(subtotal_general + envio_final + recargo_payphone, 2)
                    es_compra_mayorista = any(total_pares_carrito >= it["min_may"] for it in st.session_state.carrito)
                    puntos_ganados = 0 if es_compra_mayorista else int(subtotal_general // 50) * 10
                    
                    fecha_actual_str = ahora_ecuador().strftime("%d/%m/%Y %H:%M")
                    num_orden_unico = f"ORD-{ahora_ecuador().strftime('%m%d')}-{random.randint(1000, 9999)}"
                    
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
                    pdf_base64_str = base64.b64encode(pdf_generado).decode("utf-8")
                    
                    # Enviar automáticamente la orden, el PDF en base64 y el cliente al Google Sheet en estado PENDIENTE
                    items_para_stock = []
                    for it in carrito_copia:
                        p_u_env = it["precio_may"] if total_pares_carrito >= it["min_may"] else it["precio_ofe"]
                        items_para_stock.append({
                            "modelo": it["modelo"],
                            "color": it["color"],
                            "talla": it["talla"],
                            "cantidad": it["cantidad"],
                            "precio_unitario": round(float(p_u_env), 2),
                            "subtotal": round(float(p_u_env) * int(it["cantidad"]), 2),
                            "es_mayorista": es_compra_mayorista
                        })
                    enviar_a_google_sheet({
                        "accion": "nuevo_pedido",
                        "num_orden": num_orden_unico,
                        "fecha": fecha_actual_str,
                        "cedula": normalizar_id(cedula),
                        "cliente": f"{nombres} {apellidos}".strip(),
                        "celular": normalizar_id(celular),
                        "provincia": provincia_elegida,
                        "canton": canton_elegido,
                        "direccion": direccion,
                        "courier": courier,
                        "detalle_texto": " | ".join(lineas_productos),
                        "items_json": items_para_stock,
                        "total_pares": total_pares_carrito,
                        "subtotal": subtotal_general,
                        "envio": envio_final,
                        "recargo_pp": recargo_payphone,
                        "total": total_pagar,
                        "metodo_pago": metodo_pago,
                        "guardar_fidelidad": guardar_fidelidad,
                        "es_mayorista": es_compra_mayorista,
                        "pdf_nombre": f"{num_orden_unico}.pdf",
                        "pdf_base64": pdf_base64_str
                    })
                    st.cache_data.clear()

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
                        "es_mayorista": es_compra_mayorista,
                        "pdf_bytes": pdf_generado
                    }

            # Mostrar la Orden Confirmada de forma persistente (no desaparece al descargar el PDF)
            if st.session_state.orden_confirmada is not None:
                oc = st.session_state.orden_confirmada
                dc = oc["datos_cli"]
                
                if oc.get("es_mayorista"):
                    st.success(f"🎉 ¡Orden #{oc['num_orden']} lista, {dc['nombres']}! Se aplicó precio mayorista (las compras mayoristas no acumulan puntos de fidelidad).")
                elif oc["puntos"] > 0:
                    st.success(f"🎉 ¡Orden #{oc['num_orden']} lista, {dc['nombres']}! Con esta compra sumas **{oc['puntos']} puntos** en el Club de Fidelidad (10 puntos por cada $50).")
                else:
                    st.success(f"🎉 ¡Orden #{oc['num_orden']} lista, {dc['nombres']}! Recuerda que acumulas 10 puntos por cada $50 en compras al detal.")
                
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
                    st.write(f"**Subtotal ({oc['total_pares']} pares):** ${oc['subtotal']:.2f}")
                    st.write(f"**Costo de Envío ({dc['canton']}):** ${oc['envio']:.2f}")
                    if oc["recargo_pp"] > 0:
                        st.write(f"**Comisión Tarjeta PayPhone (6%):** ${oc['recargo_pp']:.2f}")
                    st.markdown(f"### 💰 Total a Pagar: **${oc['total']:.2f}**")
                    
                    # MOSTRAR CUENTAS BANCARIAS ÚNICAMENTE SI CONFIRMÓ LA COMPRA POR TRANSFERENCIA
                    if "Transferencia" in dc["metodo_pago"]:
                        st.markdown("---")
                        st.markdown("#### 🏦 Datos Bancarios para Transferencia / Depósito")
                        st.info("Realiza tu transferencia por el valor total a cualquiera de nuestras cuentas oficiales y envía el comprobante junto con tu PDF por WhatsApp.")
                        
                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            if os.path.exists("Datos Banco Pichincha.jpeg"):
                                st.image("Datos Banco Pichincha.jpeg", use_container_width=True)
                            elif os.path.exists("banco_pichincha.jpeg"):
                                st.image("banco_pichincha.jpeg", use_container_width=True)
                            else:
                                st.markdown(
                                    '<div style="background:#f5e642; color:#111827; padding:16px; border-radius:12px; font-family:sans-serif; box-shadow:0 3px 8px rgba(0,0,0,0.08);">'
                                    '<div style="text-align:right; font-weight:800; font-size:1.05rem; letter-spacing:0.5px;">BANCO PICHINCHA</div>'
                                    '<div style="margin-top:10px; font-size:0.95rem; font-weight:600;">María José Gonzales Arriaga</div>'
                                    '<div style="font-size:0.88rem;">Cédula: 1205602178</div>'
                                    '<div style="margin-top:10px; font-size:0.82rem;">No. de cuenta</div>'
                                    '<div style="font-size:1.15rem; font-weight:800;">2204179577 <span style="font-size:0.9rem; font-weight:700; margin-left:8px;">Cta. Ahorros</span></div>'
                                    '</div>',
                                    unsafe_allow_html=True
                                )
                            st.caption("📋 Copiar cuenta Banco Pichincha:")
                            st.code("2204179577", language=None)
                            
                        with b_col2:
                            if os.path.exists("Datos Banco Guayaquil.jpeg"):
                                st.image("Datos Banco Guayaquil.jpeg", use_container_width=True)
                            elif os.path.exists("banco_guayaquil.jpeg"):
                                st.image("banco_guayaquil.jpeg", use_container_width=True)
                            else:
                                st.markdown(
                                    '<div style="background:#d92b85; color:#ffffff; padding:16px; border-radius:12px; font-family:sans-serif; box-shadow:0 3px 8px rgba(0,0,0,0.08);">'
                                    '<div style="text-align:right; font-weight:800; font-size:1.05rem; letter-spacing:0.5px;">BANCO GUAYAQUIL</div>'
                                    '<div style="margin-top:10px; font-size:0.95rem; font-weight:600;">María José Gonzales Arriaga</div>'
                                    '<div style="font-size:0.88rem;">Cédula: 1205602178</div>'
                                    '<div style="margin-top:10px; font-size:0.82rem;">No. de cuenta</div>'
                                    '<div style="font-size:1.15rem; font-weight:800;">22751072 <span style="font-size:0.9rem; font-weight:700; margin-left:8px;">Cta. Ahorros</span></div>'
                                    '</div>',
                                    unsafe_allow_html=True
                                )
                            st.caption("📋 Copiar cuenta Banco Guayaquil:")
                            st.code("22751072", language=None)
                            
                        st.caption("🪪 Copiar cédula del titular (María José Gonzales Arriaga):")
                        st.code("1205602178", language=None)
                        st.markdown("---")
                    
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
                        f"¡Hola *Mary's Store EC*! 👠👟\n"
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
                    
                    url_wa = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(mensaje_wa)}"
                    
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
                            f"¡Hola *Mary's Store EC*! 💳\n"
                            f"Solicito el *Link de Pago PayPhone* por el valor total de *${oc['total']:.2f}* (incluye 6% comisión pasarela) correspondiente a mi Orden *#{oc['num_orden']}*:\n\n"
                            f"• *Cliente:* {dc['nombres']} {dc['apellidos']} (C.I.: {dc['cedula']})\n"
                            f"• *Destino:* {dc['provincia']} - {dc['canton']} ({dc['direccion']})\n"
                            f"• *Detalle de artículos:*\n{detalle_wa_str}\n\n"
                            f"Quedo atento/a al enlace de PayPhone para realizar el pago."
                        )
                        url_pp = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(mensaje_pp)}"
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
        ced_u_norm = normalizar_id(u["cedula"])
        
        # Refrescar puntos y pares en vivo desde el Sheet
        puntos_actuales = u.get("puntos", 0)
        pares_actuales = u.get("pares", 0)
        if not df_cli.empty and "Cédula" in df_cli.columns:
            m_act = df_cli[df_cli["Cédula"].apply(normalizar_id) == ced_u_norm]
            if not m_act.empty:
                puntos_actuales = limpiar_numero_int(m_act.iloc[0].get("Puntos Fidelidad", puntos_actuales), puntos_actuales)
                pares_actuales = limpiar_numero_int(m_act.iloc[0].get("Pares Acumulados", pares_actuales), pares_actuales)

        st.success(f"👋 ¡Bienvenido/a de nuevo, **{u['nombres']}**! (Cédula: {ced_u_norm})")
        
        c_p1, c_p2 = st.columns([1, 2], gap="large")
        with c_p1:
            with st.container(border=True):
                st.subheader("⭐ Tu Club de Fidelidad")
                st.metric("Puntos Acumulados", f"{puntos_actuales} Puntos")
                st.metric("Pares Comprados", f"{pares_actuales} Pares")
                st.info("🎁 **Meta 50 Puntos:** Por cada **$50** en compras al detal acumulas **10 puntos** (no aplica a compras mayoristas). Al llegar a 50 puntos ganas un **Envío Gratis** o acceso a **Promoción 2x1** coordinando por WhatsApp 0959276539.")
                if st.button("🔒 Cerrar Sesión", use_container_width=True):
                    st.session_state.usuario_logueado = None
                    st.rerun()
        with c_p2:
            with st.container(border=True):
                st.subheader("📦 Mi Historial de Pedidos")
                if not df_ped.empty and "Cédula Cliente" in df_ped.columns:
                    mis_pedidos = df_ped[df_ped["Cédula Cliente"].apply(normalizar_id) == ced_u_norm].copy()
                    if not mis_pedidos.empty:
                        renombres_hist = {}
                        if "Confirmación de Venta" in mis_pedidos.columns:
                            renombres_hist["Confirmación de Venta"] = "Confirmación de Pago"
                        if "Número de Guía" in mis_pedidos.columns and "Número Guía" not in mis_pedidos.columns:
                            renombres_hist["Número de Guía"] = "Número Guía"
                        if renombres_hist:
                            mis_pedidos = mis_pedidos.rename(columns=renombres_hist)

                        orden_columnas_hist = [
                            "Fecha",
                            "Código Pedido",
                            "Confirmación de Pago",
                            "Estatus Pedido",
                            "Número Guía",
                            "Detalle Artículos",
                            "Total Pares",
                            "Subtotal Calzado",
                            "Costo Envío",
                            "Comisión PayPhone",
                            "Total Final",
                            "Método Pago",
                            "Celular",
                            "Provincia",
                            "Cantón",
                            "Dirección",
                            "Courier"
                        ]
                        for col_req in orden_columnas_hist:
                            if col_req not in mis_pedidos.columns:
                                mis_pedidos[col_req] = ""
                        st.dataframe(mis_pedidos[orden_columnas_hist], use_container_width=True, hide_index=True)
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
                    ced_l_norm = normalizar_id(ced_l)
                    cor_l_clean = limpiar_texto_campo(cor_l).lower()
                    pas_l_clean = limpiar_texto_campo(pas_l)
                    
                    if not (ced_l_norm and cor_l_clean and pas_l_clean):
                        st.error("⚠️ Ingresa tu cédula, correo y contraseña para iniciar sesión.")
                    elif not df_cli.empty and "Cédula" in df_cli.columns:
                        m_cli = df_cli[df_cli["Cédula"].apply(normalizar_id) == ced_l_norm]
                        if not m_cli.empty:
                            fila_u = m_cli.iloc[0]
                            pass_guardada = limpiar_texto_campo(fila_u.get("Contraseña", ""))
                            correo_guardado = limpiar_texto_campo(fila_u.get("Correo", "")).lower()
                            
                            if not pass_guardada:
                                st.warning(
                                    "🔎 Encontramos tu cédula registrada de una compra anterior, pero aún no has creado una contraseña. "
                                    "Completa tus datos en **'Crear Cuenta'** (a la derecha) con esta misma cédula para activar tu acceso y ver tu historial completo."
                                )
                            elif pas_l_clean != pass_guardada or (correo_guardado and cor_l_clean != correo_guardado):
                                st.error("❌ El correo electrónico o la contraseña no coinciden con los registrados para esta cédula.")
                            else:
                                st.session_state.usuario_logueado = {
                                    "cedula": ced_l_norm,
                                    "nombres": limpiar_texto_campo(fila_u.get("Nombres y Apellidos", "Cliente VIP")) or "Cliente VIP",
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
                st.caption("¿Ya guardaste tus datos en una compra anterior? Verifica tu cédula para recuperar tu historial y puntos.")
                
                rc1, rc2 = st.columns([2.2, 1.2], vertical_alignment="bottom")
                with rc1:
                    ced_check_reg = st.text_input("🔍 Verificar Cédula previa (opcional):", placeholder="Ej: 0951241900", key="ced_check_reg_input")
                with rc2:
                    if st.button("Buscar datos", use_container_width=True, key="btn_check_reg"):
                        ced_chk_norm = normalizar_id(ced_check_reg)
                        if ced_chk_norm and not df_cli.empty and "Cédula" in df_cli.columns:
                            m_prev = df_cli[df_cli["Cédula"].apply(normalizar_id) == ced_chk_norm]
                            if not m_prev.empty:
                                fp = m_prev.iloc[0]
                                if limpiar_texto_campo(fp.get("Contraseña", "")):
                                    st.warning("Esta cédula ya tiene una cuenta activa con contraseña. Inicia sesión en el panel izquierdo.")
                                else:
                                    pts_prev = limpiar_numero_int(fp.get("Puntos Fidelidad", 0), 0)
                                    st.session_state.registro_autocompletado = {
                                        "cedula": ced_chk_norm,
                                        "nombres": limpiar_texto_campo(fp.get("Nombres y Apellidos", "")),
                                        "celular": normalizar_id(fp.get("Celular", "")),
                                        "correo": limpiar_texto_campo(fp.get("Correo", ""))
                                    }
                                    st.success(f"✅ ¡Encontramos tu registro previo ({pts_prev} pts)! Solo completa tu correo y crea tu contraseña abajo.")
                            else:
                                st.info("Cédula nueva. Completa tus datos en el formulario de abajo.")
                                st.session_state.registro_autocompletado = {"cedula": ced_chk_norm}

                ra = st.session_state.registro_autocompletado
                with st.form("form_registro_cliente"):
                    ced_r = st.text_input("🪪 Número de Cédula (ID Único) *", value=ra.get("cedula", ""))
                    nom_r = st.text_input("👤 Nombres y Apellidos *", value=ra.get("nombres", ""))
                    cel_r = st.text_input("📱 Celular (WhatsApp) *", value=ra.get("celular", ""))
                    cor_r = st.text_input("📧 Correo Electrónico *", value=ra.get("correo", ""))
                    pas_r = st.text_input("🔒 Crear Contraseña *", type="password")
                    acepta_datos = st.checkbox("✅ Acepto el uso y tratamiento de mis datos personales para la gestión de pedidos y el Programa de Fidelidad de Mary's Store EC.")
                    btn_reg = st.form_submit_button("Crear mi Cuenta", type="primary", use_container_width=True)
                if btn_reg:
                    ced_r_norm = normalizar_id(ced_r)
                    cel_r_norm = normalizar_id(cel_r)
                    if not (ced_r_norm and nom_r and cel_r_norm and cor_r and pas_r):
                        st.error("⚠️ Completa todos los campos obligatorios.")
                    elif not acepta_datos:
                        st.error("⚠️ Debes aceptar el uso y manejo de datos personales para crear tu cuenta.")
                    else:
                        # Verificar si la cédula ya existía (de compras anteriores) para enlazar su trazabilidad sin duplicar
                        puntos_previos = 0
                        pares_previos = 0
                        ya_tiene_cuenta = False
                        if not df_cli.empty and "Cédula" in df_cli.columns:
                            m_exist = df_cli[df_cli["Cédula"].apply(normalizar_id) == ced_r_norm]
                            if not m_exist.empty:
                                fila_ex = m_exist.iloc[0]
                                if limpiar_texto_campo(fila_ex.get("Contraseña", "")):
                                    ya_tiene_cuenta = True
                                else:
                                    puntos_previos = limpiar_numero_int(fila_ex.get("Puntos Fidelidad", 0), 0)
                                    pares_previos = limpiar_numero_int(fila_ex.get("Pares Acumulados", 0), 0)

                        if ya_tiene_cuenta:
                            st.error("⚠️ Esta cédula ya tiene una cuenta registrada. Por favor inicia sesión en el panel de la izquierda.")
                        else:
                            enviar_a_google_sheet({
                                "accion": "registro_cliente",
                                "cedula": ced_r_norm,
                                "nombres": str(nom_r).strip(),
                                "celular": cel_r_norm,
                                "correo": str(cor_r).strip(),
                                "password": str(pas_r).strip()
                            })
                            st.cache_data.clear()
                            st.session_state.registro_autocompletado = {}
                            st.session_state.usuario_logueado = {
                                "cedula": ced_r_norm,
                                "nombres": str(nom_r).strip(),
                                "puntos": puntos_previos,
                                "pares": pares_previos
                            }
                            st.success("🎉 ¡Cuenta activada con éxito! Ya puedes ver tus puntos y todo tu historial de pedidos.")
                            st.rerun()

# ==============================================================================
# VISTA 5: INFORMACIÓN DE PAGOS, ENVÍOS Y PROGRAMA DE FIDELIDAD
# ==============================================================================
elif st.session_state.vista_actual == "INFO":
    st.markdown('<div class="category-banner-black">INFORMACIÓN DE PAGOS, ENVÍOS Y FIDELIDAD</div>', unsafe_allow_html=True)
    
    ic1, ic2 = st.columns(2, gap="large")
    with ic1:
        with st.container(border=True):
            st.subheader("💳 Cómo Funcionan Nuestros Pagos y Envíos")
            st.markdown("""
            1. **Transferencia o Depósito Bancario (Sin Recargo):**
               Al confirmar tu pedido en el carrito, verás nuestras cuentas oficiales de Banco Pichincha y Banco Guayaquil, descargas tu Nota de Pedido en PDF y la envías con un clic a nuestro WhatsApp (**0959276539**) junto con tu comprobante.
            2. **Tarjeta de Crédito o Débito vía PayPhone:**
               Aceptamos tarjetas Visa y Mastercard a través de **PayPhone**. De acuerdo con las políticas de PayPhone, los cobros con tarjeta aplican una comisión de pasarela del **5% + IVA (6% total)**, valor que se detalla automáticamente en cada producto y en tu carrito.
            3. **Envíos a Todo el Ecuador:**
               Realizamos despachos seguros mediante **Servientrega** o **Cooperativa de Transporte Interprovincial**. La tarifa de envío se calcula automáticamente según tu provincia y cantón al confirmar tu orden.
            """)
    with ic2:
        with st.container(border=True):
            st.subheader("⭐ Programa de Fidelidad (Cédula Única)")
            st.markdown("""
            **¿Por qué es importante registrar tus datos y tu Cédula al comprar?**
            - Tu **Número de Cédula** es tu identificador único en nuestro sistema.
            - Por cada **$50** en tu compra al detal, acumulas **10 Puntos de Fidelidad** *(no aplica a compras mayoristas)*.
            - Al alcanzar **50 puntos**, desbloqueas una recompensa especial a tu elección:
              - 🚚 **Un Envío Nacional 100% GRATIS**, o
              - 👠 **Promoción especial 2x1** en modelos seleccionados de temporada.
            
            ⚠️ **Importante:** El canje de puntos por envío gratis o 2x1 se realiza **únicamente en coordinación directa vía WhatsApp (0959276539)** con la tienda al momento de validar tu pedido.
            """)

# ==============================================================================
# PIE DE PÁGINA COMPACTO Y MODERNO
# ==============================================================================
st.markdown(f"""
<div class="store-footer">
    <div class="footer-copy">
        © {ahora_ecuador().year} <strong>Mary's Store EC</strong> • Envíos a todo el Ecuador
    </div>
    <div class="footer-socials">
        <a href="{URL_FACEBOOK}" target="_blank" class="footer-link"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M22.675 0h-21.35c-.732 0-1.325.593-1.325 1.325v21.351c0 .731.593 1.324 1.325 1.324h11.495v-9.294h-3.128v-3.622h3.128v-2.671c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12v9.293h6.116c.73 0 1.323-.593 1.323-1.325v-21.35c0-.732-.593-1.325-1.325-1.325z"/></svg> Facebook</a>
        <a href="{URL_INSTAGRAM}" target="_blank" class="footer-link"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg> Instagram</a>
        <a href="https://wa.me/{WHATSAPP_NUMERO}" target="_blank" class="footer-link"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/></svg> WhatsApp</a>
    </div>
</div>
""", unsafe_allow_html=True)
