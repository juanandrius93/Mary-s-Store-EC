import streamlit as st
import pandas as pd
import urllib.parse
import re
import os
import random
import uuid
import datetime
from datetime import datetime
from fpdf import FPDF

# ---------------------------------------------------------
# 1. Configuración e Inicialización
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mary's Store Ec & Babayork Urban | Tienda Oficial",
    page_icon="👠",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }
    .top-utility-bar { display: flex; justify-content: flex-end; gap: 20px; font-size: 0.78rem; color: #4b5563; border-bottom: 1px solid #f3f4f6; padding-bottom: 6px; margin-bottom: 12px; font-weight: 500; text-transform: uppercase; }
    .top-utility-highlight { color: #e11d48; font-weight: 700; }
    .category-banner-black { background-color: #1a1a1a; color: #ffffff; padding: 18px 28px; font-size: 1.65rem; font-weight: 400; letter-spacing: 2px; text-transform: uppercase; margin-top: 8px; margin-bottom: 12px; }
    .product-img-wrapper { position: relative; background-color: #f9fafb; border-radius: 4px; overflow: hidden; margin-bottom: 10px; text-align: center; cursor: pointer; }
    .product-img-wrapper img { width: 100%; height: 270px; object-fit: cover; display: block; transition: transform 0.3s ease; }
    .product-img-wrapper img:hover { transform: scale(1.03); }
    .badge-discount { position: absolute; top: 10px; right: 10px; background-color: #e11d48; color: #ffffff; padding: 4px 9px; font-size: 0.78rem; font-weight: 700; border-radius: 2px; z-index: 2; }
    .product-title { font-size: 0.98rem; color: #1f2937; font-weight: 600; margin: 4px 0 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .price-offer { color: #e11d48; font-size: 1.25rem; font-weight: 800; margin-right: 8px; }
    .price-regular { text-decoration: line-through; color: #9ca3af; font-size: 0.92rem; }
    .price-wholesale { background-color: #fffbeb; border: 1px solid #fde68a; color: #b45309; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: 600; display: inline-block; margin-top: 4px; margin-bottom: 8px; }
    .whatsapp-btn { display: block; background-color: #25D366; color: white !important; text-align: center; padding: 14px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1.05rem; margin-top: 12px; }
    .card-btn { display: block; background-color: #1d4ed8; color: white !important; text-align: center; padding: 14px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1.05rem; margin-top: 10px; }
    .payphone-fee-note { font-size: 0.8rem; color: #6b7280; font-style: italic; margin-top: 4px;}
</style>
""", unsafe_allow_html=True)

if "carrito" not in st.session_state: st.session_state.carrito = []
if "vista_actual" not in st.session_state: st.session_state.vista_actual = "DETAL"
if "cat_menu" not in st.session_state: st.session_state.cat_menu = "TODAS"
if "usuario_logueado" not in st.session_state: st.session_state.usuario_logueado = None
if "producto_seleccionado" not in st.session_state: st.session_state.producto_seleccionado = None

# ---------------------------------------------------------
# 2. Funciones de Limpieza y Utilidades
# ---------------------------------------------------------
def limpiar_numero_float(valor, por_defecto=0.0):
    if pd.isna(valor): return float(por_defecto)
    texto = str(valor).strip()
    if not texto: return float(por_defecto)
    texto = re.sub(r"[^0-9,.-]", "", texto)
    if "," in texto and "." not in texto: texto = texto.replace(",", ".")
    elif "," in texto and "." in texto: texto = texto.replace(",", "")
    try: return float(texto)
    except Exception: return float(por_defecto)

def limpiar_numero_int(valor, por_defecto=0):
    return int(round(limpiar_numero_float(valor, por_defecto)))

def preparar_url_imagen(url):
    if pd.isna(url) or not str(url).strip(): return "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"
    url_str = str(url).strip()
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url_str)
    if not match: match = re.search(r"id=([a-zA-Z0-9_-]+)", url_str)
    if match and "drive.google.com" in url_str: return f"https://drive.google.com/thumbnail?id={match.group(1)}&sz=w800"
    return url_str

# ---------------------------------------------------------
# 3. Conexión con Google Sheets (Lectura de las 4 pestañas)
# ---------------------------------------------------------
SHEET_ID = "1LGRa-BfRkiRbyqukW0aWWpHJh2tKV_W-IgB0SRbx8N0"
URL_INV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Inventario"
URL_CLI = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Fidelidad_Clientes"
URL_ENV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Costos_Envio"
URL_PED = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Ventas_Historial"

@st.cache_data(ttl=15)
def cargar_datos(url, tipo="inv"):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if not df.empty: return df
    except Exception: pass
    
    if tipo == "inv":
        return pd.DataFrame([
            {"Modelo": "Tanara Botas Taco Cuadrado", "Categoría": "Botas", "Material": "Cuero Sintético", "Color": "Animal Print", "Precio Regular ($)": 99.99, "Precio Oferta ($)": 99.99, "Precio Mayorista ($)": 75.00, "Mínimo Mayorista": 3, "En Oferta": "No", "Talla 34": 2, "Talla 35": 3, "Talla 36": 5, "Talla 37": 4, "Talla 38": 3, "Talla 39": 2, "Talla 40": 1, "Enlace Imagen": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"},
            {"Modelo": "Hey Dude Hudson Lift", "Categoría": "Deportivos", "Material": "Malla", "Color": "Rosa", "Precio Regular ($)": 95.99, "Precio Oferta ($)": 95.99, "Precio Mayorista ($)": 70.00, "Mínimo Mayorista": 3, "En Oferta": "No", "Talla 34": 1, "Talla 35": 2, "Talla 36": 2, "Talla 37": 0, "Talla 38": 1, "Talla 39": 1, "Talla 40": 0, "Enlace Imagen": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111"}
        ])
    elif tipo == "envios":
        return pd.DataFrame([
            {"Provincia": "Los Ríos", "Cantón": "Babahoyo", "Costo ($)": 0.00},
            {"Provincia": "Guayas", "Cantón": "Guayaquil", "Costo ($)": 4.50},
            {"Provincia": "Pichincha", "Cantón": "Quito", "Costo ($)": 5.50},
            {"Provincia": "Azuay", "Cantón": "Cuenca", "Costo ($)": 6.00}
        ])
    else: return pd.DataFrame()

df_inv = cargar_datos(URL_INV, "inv")
df_envios = cargar_datos(URL_ENV, "envios")
df_cli = cargar_datos(URL_CLI, "cli")

# ---------------------------------------------------------
# 4. Generador PDF
# ---------------------------------------------------------
def generar_pdf_pedido(num_orden, cl, carrito, envio, subtotal, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "MARY'S STORE EC & BABAYORK URBAN", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"ORDEN: {num_orden} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    def limpiar(txt): return str(txt).encode("latin-1", "replace").decode("latin-1")
    
    pdf.cell(0, 6, limpiar(f"Cliente: {cl['nombres']} {cl['apellidos']} (CI: {cl['cedula']})"), ln=True)
    pdf.cell(0, 6, limpiar(f"Lugar: {cl['provincia']} - {cl['canton']} | Dir: {cl['direccion']}"), ln=True)
    pdf.cell(0, 6, limpiar(f"Pago: {cl['metodo_pago']}"), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(85, 8, "Articulo", 1, 0)
    pdf.cell(20, 8, "Talla", 1, 0, "C")
    pdf.cell(20, 8, "Cant", 1, 0, "C")
    pdf.cell(30, 8, "Subtotal", 1, 1, "R")
    
    pdf.set_font("Helvetica", "", 10)
    for i in carrito:
        pdf.cell(85, 8, limpiar(f"{i['modelo']} ({i['color']})")[:40], 1, 0)
        pdf.cell(20, 8, i['talla'], 1, 0, "C")
        pdf.cell(20, 8, str(i['cantidad']), 1, 0, "C")
        pdf.cell(30, 8, f"${i['subtotal']:.2f}", 1, 1, "R")
        
    pdf.ln(5)
    pdf.cell(125, 6, "Subtotal:", 0, 0, "R")
    pdf.cell(30, 6, f"${subtotal:.2f}", 0, 1, "R")
    pdf.cell(125, 6, "Costo de Envio:", 0, 0, "R")
    pdf.cell(30, 6, f"${envio:.2f}", 0, 1, "R")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(125, 8, "TOTAL:", 0, 0, "R")
    pdf.cell(30, 8, f"${total:.2f}", 0, 1, "R")
    return bytes(pdf.output())

# ---------------------------------------------------------
# 5. Interfaz: Cabecera y Navegación
# ---------------------------------------------------------
st.markdown("""
<div class="top-utility-bar">
    <span>🚚 ENVÍOS CONFIGURABLES POR PROVINCIA</span> | 
    <span>📍 BABAHOYO: PAGO CONTRAENTREGA</span> | 
    <span class="top-utility-highlight">⭐ FIDELIDAD: 0959276539</span>
</div>
""", unsafe_allow_html=True)

h1, h2, h3, h4 = st.columns([1, 1.2, 4.3, 2.5], vertical_alignment="center")
with h1:
    if os.path.exists("logo_marys.jpg"): st.image("logo_marys.jpg", width=120)
    else: st.markdown("### Mary's Store")
with h2:
    if os.path.exists("logo_babayork.jpg"): st.image("logo_babayork.jpg", width=90)
    else: st.markdown("#### BABAYORK")
with h3:
    busqueda = st.text_input("Buscador", placeholder="🔍 Busca modelo, color, material...", label_visibility="collapsed")
with h4:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👤 Mi Cuenta", use_container_width=True):
            st.session_state.vista_actual = "LOGIN"
            st.rerun()
    with c2:
        if st.button("📦 Mayoristas", use_container_width=True):
            st.session_state.vista_actual = "MAYORISTA"
            st.rerun()
    with c3:
        if st.button(f"🛒 Carrito ({sum(i['cantidad'] for i in st.session_state.carrito)})", use_container_width=True, type="primary"):
            st.session_state.vista_actual = "CARRITO"
            st.rerun()

st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)

categorias = sorted([str(c) for c in df_inv["Categoría"].dropna().unique()])
nav_opts = ["TODAS"] + [c.upper() for c in categorias] + ["ℹ️ INFO & PAGOS"]
cols_nav = st.columns(len(nav_opts))
for i, op in enumerate(nav_opts):
    with cols_nav[i]:
        if st.button(op, use_container_width=True, type="primary" if st.session_state.cat_menu == op and st.session_state.vista_actual in ["DETAL", "MAYORISTA"] else "secondary"):
            if op == "ℹ️ INFO & PAGOS": st.session_state.vista_actual = "INFO"
            else:
                st.session_state.vista_actual = "DETAL"
                st.session_state.cat_menu = op
            st.session_state.producto_seleccionado = None
            st.rerun()

# ---------------------------------------------------------
# VISTA: MI CUENTA / INICIAR SESIÓN
# ---------------------------------------------------------
if st.session_state.vista_actual == "LOGIN":
    st.markdown('<div class="category-banner-black">MI CUENTA Y FIDELIDAD</div>', unsafe_allow_html=True)
    if st.session_state.usuario_logueado:
        u = st.session_state.usuario_logueado
        st.success(f"¡Bienvenido(a), {u['nombres']}!")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Tus Puntos de Fidelidad")
            st.metric("Puntos Acumulados", f"{u.get('Puntos Fidelidad', 0)} pts")
            st.write("Recuerda: 50 puntos = 1 Envío Gratis o promoción 2x1.")
        with col2:
            st.subheader("Historial de Pedidos")
            st.info("Aquí puedes ver tus órdenes registradas en el sistema.")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_logueado = None
            st.rerun()
    else:
        col_log, col_reg = st.columns(2, gap="large")
        with col_log:
            st.subheader("Iniciar Sesión")
            with st.form("form_login"):
                ced_log = st.text_input("Número de Cédula")
                pass_log = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Ingresar", type="primary"):
                    if not df_cli.empty and "Cédula" in df_cli.columns:
                        match = df_cli[df_cli["Cédula"].astype(str) == str(ced_log)]
                        if not match.empty:
                            st.session_state.usuario_logueado = {
                                "cedula": ced_log,
                                "nombres": match.iloc[0].get("Nombres y Apellidos", "Cliente"),
                                "Puntos Fidelidad": match.iloc[0].get("Puntos Fidelidad", 0)
                            }
                            st.rerun()
                        else: st.error("Cédula no encontrada. Por favor regístrate.")
                    else: st.error("Sistema de base de datos en mantenimiento.")
        with col_reg:
            st.subheader("Crear Cuenta Nueva")
            with st.form("form_registro"):
                ced_reg = st.text_input("Cédula")
                nom_reg = st.text_input("Nombres Completos")
                mail_reg = st.text_input("Correo Electrónico")
                pass_reg = st.text_input("Crea una Contraseña", type="password")
                acepta = st.checkbox("Acepto el uso y manejo de datos personales para compras y fidelidad.")
                if st.form_submit_button("Registrarme"):
                    if acepta and ced_reg:
                        st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                    else: st.error("Debes aceptar las políticas y llenar los datos obligatorios.")

# ---------------------------------------------------------
# VISTA: INFO
# ---------------------------------------------------------
elif st.session_state.vista_actual == "INFO":
    st.markdown('<div class="category-banner-black">INFORMACIÓN Y CLUB DE FIDELIDAD</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 💳 Pagos y Comisiones (PayPhone)")
        st.write("Aceptamos Transferencias, Depósitos y Pago Contraentrega (solo Babahoyo) sin recargo.")
        st.warning("**Pagos con Tarjeta (PayPhone):** Según políticas de la pasarela, los pagos con tarjeta de crédito/débito generan un recargo del **6% (5% + IVA) por procesamiento**. Este valor se sumará automáticamente a tu total si eliges este método en el carrito.")
    with c2:
        st.markdown("### ⭐ Club de Fidelidad")
        st.write("Regístrate o marca la casilla al comprar para guardar tus datos con tu Cédula.")
        st.write("- Ganas 10 puntos por par.")
        st.write("- **Al llegar a 50 puntos:** ¡Envío GRATIS o aplica 2x1! (Coordinación exclusiva vía WhatsApp).")

# ---------------------------------------------------------
# VISTA: DETALLE DE PRODUCTO
# ---------------------------------------------------------
elif st.session_state.producto_seleccionado:
    prod = st.session_state.producto_seleccionado
    if st.button("⬅️ Volver al catálogo"):
        st.session_state.producto_seleccionado = None
        st.rerun()
        
    c_img, c_det = st.columns([1, 1])
    with c_img:
        st.image(prod["imagen"], use_container_width=True)
    with c_det:
        st.markdown(f"<h2>{prod['modelo']}</h2>", unsafe_allow_html=True)
        st.write(f"**Categoría:** {prod['categoria']} | **Color:** {prod['color']}")
        
        p_ofe = prod["p_ofe"]
        p_tarjeta = round(p_ofe * 1.06, 2)
        
        st.markdown(f"""
        <div style='background-color:#f8fafc; padding:15px; border-radius:8px; margin-bottom:15px;'>
            <div style='font-size:1.4rem; font-weight:bold; color:#1e293b;'>Precio Transferencia / Efectivo: <span style='color:#e11d48;'>${p_ofe:.2f}</span></div>
            <div style='font-size:1rem; color:#64748b; margin-top:5px;'>Precio con Tarjeta (PayPhone): ${p_tarjeta:.2f} <span style='font-size:0.8rem;'>(Incluye 6% com. pasarela)</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        talla_sel = st.selectbox("Selecciona tu Talla:", ["34", "35", "36", "37", "38", "39", "40"])
        stock = 5
        
        if stock > 0:
            st.markdown("<div class='stock-ok'>✅ En Stock</div>", unsafe_allow_html=True)
            cant = st.number_input("Cantidad", min_value=1, max_value=stock)
            if st.button("AÑADIR AL CARRITO", type="primary", use_container_width=True):
                st.session_state.carrito.append({
                    "modelo": prod["modelo"], "categoria": prod["categoria"], "color": prod["color"],
                    "talla": talla_sel, "cantidad": cant, "precio_ofe": p_ofe, "precio_may": prod["p_may"],
                    "min_may": prod["min_may"], "imagen": prod["imagen"], "subtotal": p_ofe * cant
                })
                st.toast("¡Añadido al carrito!")
        else:
            st.markdown("<div class='stock-zero'>❌ Agotado</div>", unsafe_allow_html=True)
            
        with st.expander("📏 Ver Guía de Tallas"):
            st.markdown("""
            | Talla | Centímetros |
            |-------|-------------|
            | 34    | 22.5 cm     |
            | 35    | 23.0 cm     |
            | 36    | 23.5 cm     |
            | 37    | 24.0 cm     |
            | 38    | 24.5 cm     |
            | 39    | 25.5 cm     |
            | 40    | 26.0 cm     |
            """)

# ---------------------------------------------------------
# VISTA: CATÁLOGO Y FILTROS
# ---------------------------------------------------------
elif st.session_state.vista_actual in ["DETAL", "MAYORISTA"]:
    es_mayor = (st.session_state.vista_actual == "MAYORISTA")
    tit = "MAYORISTAS" if es_mayor else ("TODO EL CALZADO" if st.session_state.cat_menu == "TODAS" else st.session_state.cat_menu)
    st.markdown(f'<div class="category-banner-black">{tit}</div>', unsafe_allow_html=True)
    
    cs, cc = st.columns([1, 4])
    with cs:
        st.write("**FILTROS**")
        t_f = st.selectbox("Talla", ["Todas", "34", "35", "36", "37", "38", "39", "40"])
    
    with cc:
        df_m = df_inv.copy()
        if st.session_state.cat_menu != "TODAS": df_m = df_m[df_m["Categoría"].astype(str).str.upper() == st.session_state.cat_menu]
        if busqueda: df_m = df_m[df_m["Modelo"].astype(str).str.contains(busqueda, case=False, na=False)]
        
        mods = list(df_m["Modelo"].dropna().unique())
        cols_g = st.columns(3)
        
        for i, m_name in enumerate(mods):
            v_mod = df_m[df_m["Modelo"] == m_name]
            with cols_g[i % 3]:
                with st.container(border=True):
                    f0 = v_mod.iloc[0]
                    cat = f0.get("Categoría", "")
                    colores = list(v_mod["Color"].dropna().unique())
                    
                    st.write(f"**{m_name}**")
                    col_sel = st.selectbox("Color", colores, key=f"c_{i}", label_visibility="collapsed")
                    f_c = v_mod[v_mod["Color"] == col_sel].iloc[0]
                    
                    p_reg = limpiar_numero_float(f_c.get("Precio Regular ($)", 0))
                    p_ofe = limpiar_numero_float(f_c.get("Precio Oferta ($)", 0))
                    p_may = limpiar_numero_float(f_c.get("Precio Mayorista ($)", 0))
                    m_may = limpiar_numero_int(f_c.get("Mínimo Mayorista", 6))
                    oferta_activa = str(f_c.get("En Oferta", "No")).strip().lower() == "si"
                    
                    img = preparar_url_imagen(f_c.get("Enlace Imagen"))
                    
                    st.markdown(f"<div class='product-img-wrapper'><img src='{img}'></div>", unsafe_allow_html=True)
                    if st.button("Ver Detalles", key=f"det_{i}", use_container_width=True):
                        st.session_state.producto_seleccionado = {
                            "modelo": m_name, "categoria": cat, "color": col_sel, 
                            "imagen": img, "p_ofe": p_ofe, "p_may": p_may, "min_may": m_may
                        }
                        st.rerun()
                        
                    if es_mayor: st.markdown(f"<span class='price-offer'>${p_may:.2f}</span>", unsafe_allow_html=True)
                    else:
                        if oferta_activa and p_reg > p_ofe:
                            st.markdown(f"<span class='price-offer'>${p_ofe:.2f}</span> <span class='price-regular'>${p_reg:.2f}</span>", unsafe_allow_html=True)
                        else: st.markdown(f"<span class='price-offer'>${p_reg if not oferta_activa else p_ofe:.2f}</span>", unsafe_allow_html=True)

# ---------------------------------------------------------
# VISTA: CARRITO
# ---------------------------------------------------------
elif st.session_state.vista_actual == "CARRITO":
    st.markdown('<div class="category-banner-black">CARRITO DE COMPRAS</div>', unsafe_allow_html=True)
    if not st.session_state.carrito: st.warning("Tu carrito está vacío.")
    else:
        c_res, c_chk = st.columns([1, 1.2])
        tot_pares = sum(i["cantidad"] for i in st.session_state.carrito)
        subt = 0.0
        
        with c_res:
            for i, it in enumerate(st.session_state.carrito):
                p_u = it["precio_may"] if tot_pares >= it["min_may"] else it["precio_ofe"]
                it["subtotal"] = p_u * it["cantidad"]
                subt += it["subtotal"]
                with st.container(border=True):
                    st.write(f"**{it['modelo']}** ({it['color']} - Talla {it['talla']})")
                    st.write(f"Cant: {it['cantidad']} x ${p_u:.2f} = **${it['subtotal']:.2f}**")
                    if st.button("Quitar", key=f"q_{i}"):
                        st.session_state.carrito.pop(i)
                        st.rerun()
                        
        with c_chk:
            st.subheader("Datos de Envío y Pago")
            
            with st.form("chk"):
                ced = st.text_input("Cédula")
                nom = st.text_input("Nombres y Apellidos")
                cel = st.text_input("Celular (WhatsApp)")
                
                st.text("País: Ecuador")
                
                # Provincias y Cantones dinámicos desde el Sheet Costos_Envio
                lista_prov = ["Guayas", "Pichincha", "Los Ríos"]
                if not df_envios.empty and "Provincia" in df_envios.columns:
                    lista_prov = sorted(list(df_envios["Provincia"].dropna().unique()))
                
                prov = st.selectbox("Provincia", lista_prov)
                
                cantones = ["Cantón Principal"]
                if not df_envios.empty and "Cantón" in df_envios.columns:
                    cantones = df_envios[df_envios["Provincia"] == prov]["Cantón"].tolist()
                
                canton = st.selectbox("Cantón / Ciudad", cantones)
                dir_ex = st.text_area("Dirección Exacta")
                
                mpago = st.radio("Método de Pago", ["Transferencia", "Tarjeta de Crédito / PayPhone (+6%)", "Efectivo (Solo Babahoyo)"])
                guardar = st.checkbox("Guardar mis datos y participar en el Club de Fidelidad", value=True)
                
                btn = st.form_submit_button("Confirmar Compra", type="primary", use_container_width=True)
                
            if btn:
                if not ced or not nom: st.error("Por favor completa los campos obligatorios.")
                else:
                    # Costo de envío según Sheet
                    costo_env = 5.00
                    if not df_envios.empty:
                        fila_e = df_envios[(df_envios["Provincia"] == prov) & (df_envios["Cantón"] == canton)]
                        if not fila_e.empty: costo_env = limpiar_numero_float(fila_e.iloc[0]["Costo ($)"])
                    
                    # Recargo PayPhone (+6%)
                    tarifa_pp = 0.0
                    if "Tarjeta" in mpago: tarifa_pp = round(subt * 0.06, 2)
                    
                    tot = round(subt + costo_env + tarifa_pp, 2)
                    cod = f"ORD-{random.randint(1000, 9999)}"
                    
                    st.success(f"¡Orden {cod} generada con éxito!")
                    st.write(f"Subtotal: ${subt:.2f} | Envío ({canton}): ${costo_env:.2f} | Recargo Tarjeta: ${tarifa_pp:.2f}")
                    st.markdown(f"### Total a Pagar: ${tot:.2f}")
                    st.info("💡 En producción: El stock se descontará automáticamente en Google Sheets y la orden se registrará en Ventas_Historial con estado PENDIENTE.")
                    
                    cli_d = {"cedula": ced, "nombres": nom, "apellidos": "", "celular": cel, "provincia": prov, "canton": canton, "direccion": dir_ex, "metodo_pago": mpago}
                    pdf_b = generar_pdf_pedido(cod, cli_d, st.session_state.carrito, tot_pares, subt, costo_env + tarifa_pp, tot)
                    st.download_button("Descargar Nota de Pedido (PDF)", pdf_b, f"{cod}.pdf", "application/pdf")
                    
                    msg = f"Hola, orden *{cod}*\nCliente: {nom}\nEnvío a {prov}, {canton}\nPago: {mpago}\n"
                    for it in st.session_state.carrito:
                        msg += f"- {it['cantidad']}x {it['modelo']} ({it['color']} - T{it['talla']}) = ${it['subtotal']:.2f}\n"
                    msg += f"\nTotal: ${tot:.2f}"
                    
                    if "Tarjeta" in mpago: msg += f"\n👉 Solicito Link PayPhone por ${tot:.2f} (Incluye comisiones de pasarela)."
                    st.markdown(f'<a href="https://wa.me/593959276539?text={urllib.parse.quote(msg)}" target="_blank" class="whatsapp-btn">Enviar Pedido a WhatsApp</a>', unsafe_allow_html=True)
