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

# Estilos CSS personalizados para diseño profesional de E-commerce
st.markdown("""
<style>
    .main-banner {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .price-regular {
        text-decoration: line-through;
        color: #9ca3af;
        font-size: 1rem;
        margin-right: 8px;
    }
    .price-offer {
        color: #e11d48;
        font-size: 1.5rem;
        font-weight: 800;
    }
    .price-wholesale {
        background-color: #fef3c7;
        color: #b45309;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .stock-ok {
        color: #059669;
        font-weight: 700;
        background: #d1fae5;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .stock-zero {
        color: #dc2626;
        font-weight: 700;
        background: #fee2e2;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .whatsapp-btn {
        display: block;
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 14px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 12px;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);
    }
    .card-btn {
        display: block;
        background-color: #2563eb;
        color: white !important;
        text-align: center;
        padding: 14px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar el carrito de compras en memoria de sesión
if "carrito" not in st.session_state:
    st.session_state.carrito = []

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
    
    # Encabezado de la empresa
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "MARY'S STORE EC & BABAYORK URBAN", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Tienda Oficial de Calzado | WhatsApp: 0959276539", ln=True, align="C")
    pdf.ln(5)
    
    # Datos de la Orden y Cliente
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
    
    # Tabla de productos
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
        if "Color" in df.columns and "Talla 34" in df.columns:
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

# ENCABEZADO CON LOGOS DE LA EMPRESA
col_logo1, col_titulo, col_logo2 = st.columns([1.2, 3.6, 1.2])
with col_logo1:
    if os.path.exists("logo_marys.jpg"):
        st.image("logo_marys.jpg", use_container_width=True)
    elif os.path.exists("logo_marys.png"):
        st.image("logo_marys.png", use_container_width=True)
with col_titulo:
    st.markdown("""
    <div class="main-banner">
        <h1 style="margin:0; font-size: 2rem;">Mary’s Store Ec & Babayork Urban</h1>
        <p style="margin:5px 0 0 0; font-size: 1rem; opacity: 0.9;">
            👠 Baletas • Sandalias • Tacones • Zapatillas Deportivas Hombre y Mujer 👟<br>
            🚚 Envíos seguros a todo el Ecuador | Pago contraentrega en Babahoyo
        </p>
    </div>
    """, unsafe_allow_html=True)
with col_logo2:
    if os.path.exists("logo_babayork.jpg"):
        st.image("logo_babayork.jpg", use_container_width=True)
    elif os.path.exists("logo_babayork.png"):
        st.image("logo_babayork.png", use_container_width=True)

# Barra superior de navegación rápida y contador del carrito
total_items_carrito = sum(item["cantidad"] for item in st.session_state.carrito)

modo_vista = st.radio(
    "Navegación Principal:",
    ["🛍️ Catálogo al Detal", "📦 Catálogo Mayorista", f"🛒 Mi Carrito y Pagar ({total_items_carrito})"],
    horizontal=True
)

st.markdown("---")

# ==============================================================================
# VISTA 1 Y 2: CATÁLOGO DE PRODUCTOS (ESTILO AMAZON POR COLOR Y TALLA)
# ==============================================================================
if modo_vista in ["🛍️ Catálogo al Detal", "📦 Catálogo Mayorista"]:
    es_mayorista = (modo_vista == "📦 Catálogo Mayorista")
    
    if es_mayorista:
        st.info("📦 **Zona Mayorista Activada:** Los precios al por mayor se aplican desde el mínimo de unidades indicado en cada modelo (puedes combinar tallas y colores).")
    
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        lista_categorias = ["Todas"] + sorted(list(df_inv["Categoría"].dropna().unique()))
        cat_sel = st.selectbox("📂 Filtrar por Categoría:", lista_categorias)
    with f_col2:
        busqueda = st.text_input("🔍 Buscar modelo o material (ej. Edilma, Charol, Deportivo):")

    df_mostrar = df_inv.copy()
    if cat_sel != "Todas":
        df_mostrar = df_mostrar[df_mostrar["Categoría"] == cat_sel]
    if busqueda:
        df_mostrar = df_mostrar[
            df_mostrar["Modelo"].astype(str).str.contains(busqueda, case=False, na=False) |
            df_mostrar["Material"].astype(str).str.contains(busqueda, case=False, na=False)
        ]

    modelos_unicos = df_mostrar["Modelo"].dropna().unique()

    if len(modelos_unicos) == 0:
        st.warning("No se encontraron modelos con ese filtro.")
    else:
        cols_grid = st.columns(2)
        for idx, nombre_modelo in enumerate(modelos_unicos):
            variantes_modelo = df_mostrar[df_mostrar["Modelo"] == nombre_modelo]
            
            with cols_grid[idx % 2]:
                with st.container(border=True):
                    primera_fila = variantes_modelo.iloc[0]
                    categoria_mod = primera_fila.get("Categoría", "Calzado")
                    material_mod = primera_fila.get("Material", "Estándar")
                    
                    st.subheader(f"{nombre_modelo}")
                    st.caption(f"Categoría: **{categoria_mod}** | Material: **{material_mod}**")
                    
                    c_img, c_info = st.columns([1.1, 1.3])
                    
                    with c_info:
                        colores_disp = list(variantes_modelo["Color"].dropna().unique())
                        color_elegido = st.selectbox(
                            "🎨 Selecciona el Color:",
                            colores_disp,
                            key=f"color_{nombre_modelo}_{idx}"
                        )
                        
                        fila_color = variantes_modelo[variantes_modelo["Color"] == color_elegido].iloc[0]
                        
                        p_reg = float(fila_color.get("Precio Regular ($)", 24.99))
                        p_ofe = float(fila_color.get("Precio Oferta ($)", 19.99))
                        p_may = float(fila_color.get("Precio Mayorista ($)", p_ofe * 0.75))
                        min_may = int(fila_color.get("Mínimo Mayorista", 6))
                        
                        if es_mayorista:
                            st.markdown(f"<span class='price-offer'>${p_may:.2f} c/u</span> <span class='price-regular'>${p_ofe:.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"<div class='price-wholesale'>📦 Mínimo mayorista: {min_may} pares</div>", unsafe_allow_html=True)
                            precio_aplicado = p_may
                        else:
                            st.markdown(f"<span class='price-regular'>${p_reg:.2f}</span> <span class='price-offer'>${p_ofe:.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"<div class='price-wholesale'>💡 Mayorista: ${p_may:.2f} (desde {min_may} pares)</div>", unsafe_allow_html=True)
                            precio_aplicado = p_ofe

                        tallas_lista = ["34", "35", "36", "37", "38", "39", "40"]
                        talla_elegida = st.selectbox(
                            "📏 Selecciona la Talla:",
                            tallas_lista,
                            key=f"talla_{nombre_modelo}_{idx}"
                        )
                        
                        col_talla_nombre = f"Talla {talla_elegida}"
                        stock_disponible = 0
                        if col_talla_nombre in fila_color:
                            try:
                                stock_disponible = int(float(fila_color[col_talla_nombre]))
                            except Exception:
                                stock_disponible = 0
                        
                        if stock_disponible > 0:
                            st.markdown(f"<div class='stock-ok'>✅ Disponible ({stock_disponible} en stock)</div>", unsafe_allow_html=True)
                            cant_min = min_may if (es_mayorista and stock_disponible >= min_may) else 1
                            cantidad_pedir = st.number_input(
                                "Cantidad de pares:",
                                min_value=1,
                                max_value=stock_disponible,
                                value=min(cant_min, stock_disponible),
                                step=1,
                                key=f"cant_{nombre_modelo}_{idx}"
                            )
                            
                            if st.button("🛒 Agregar al Carrito", key=f"btn_{nombre_modelo}_{idx}", use_container_width=True, type="primary"):
                                st.session_state.carrito.append({
                                    "modelo": nombre_modelo,
                                    "categoria": categoria_mod,
                                    "color": color_elegido,
                                    "talla": talla_elegida,
                                    "cantidad": cantidad_pedir,
                                    "precio_unitario": precio_aplicado,
                                    "precio_ofe": p_ofe,
                                    "precio_may": p_may,
                                    "min_may": min_may,
                                    "subtotal": round(cantidad_pedir * precio_aplicado, 2),
                                    "imagen": preparar_url_imagen(fila_color.get("Enlace Imagen"))
                                })
                                st.toast(f"✅ {nombre_modelo} ({color_elegido} - Talla {talla_elegida}) agregado al carrito.")
                                st.rerun()
                        else:
                            st.markdown("<div class='stock-zero'>❌ Agotado en este color y talla (Stock: 0)</div>", unsafe_allow_html=True)
                            st.caption("Selecciona otro color u otra talla disponible.")

                    with c_img:
                        url_limpia = preparar_url_imagen(fila_color.get("Enlace Imagen"))
                        st.image(url_limpia, use_container_width=True)

# ==============================================================================
# VISTA 3: VENTANA DEL CARRITO, DATOS DE CLIENTE (FIDELIDAD), PDF Y PAGO
# ==============================================================================
elif modo_vista.startswith("🛒 Mi Carrito"):
    st.header("🛒 Tu Carrito de Compras y Finalización de Pedido")
    
    if len(st.session_state.carrito) == 0:
        st.info("Tu carrito está vacío. Ve al catálogo, elige tus modelos, colores y tallas favoritas y agrégalos al carrito.")
    else:
        col_resumen, col_checkout = st.columns([1.2, 1.2])
        
        with col_resumen:
            st.subheader("1. Resumen de Productos Seleccionados")
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
            st.caption("Registra tus datos para el envío y acumula puntos en nuestro Club de Fidelidad.")
            
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
                
                confirmar_btn = st.form_submit_button("✅ Confirmar Datos y Generar Orden de Compra", type="primary", use_container_width=True)

            if confirmar_btn:
                if not (cedula and nombres and apellidos and celular and direccion):
                    st.error("⚠️ Por favor completa todos los campos obligatorios (*) para continuar.")
                else:
                    costo_envio = 0.0 if "Babahoyo" in courier else 5.00
                    total_pagar = round(subtotal_general + costo_envio, 2)
                    puntos_ganados = int(total_pares_carrito * 10)
                    num_orden = f"MB-{random.randint(1000, 9999)}"
                    
                    st.success(f"🎉 ¡Orden #{num_orden} generada con éxito, {nombres}! Con esta compra acumulas **{puntos_ganados} puntos** en el Club de Fidelidad.")
                    
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
                        
                        # 1. Botón de descarga de PDF
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
                        
                        # 2. Botón de envío directo a WhatsApp
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
                        
                        # 3. Módulo de Pago con Tarjeta si el cliente eligió tarjeta
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
