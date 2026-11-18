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
st.markdown('''
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }
    .top-utility-bar { display: flex; justify-content: flex-end; gap: 20px; font-size: 0.78rem; color: #4b5563; border-bottom: 1px solid #f3f4f6; padding-bottom: 6px; margin-bottom: 12px; font-weight: 500; text-transform: uppercase; }
    .top-utility-highlight { color: #e11d48; font-weight: 700; }
    
    .category-banner-black { background-color: #1a1a1a; color: #ffffff; padding: 18px 28px; font-size: 1.65rem; font-weight: 400; letter-spacing: 2px; text-transform: uppercase; margin-top: 8px; margin-bottom: 12px; text-align: center; }
    
    .product-img-wrapper { position: relative; background-color: #f9fafb; border-radius: 4px; overflow: hidden; margin-bottom: 10px; text-align: center; cursor: pointer; }
    .product-img-wrapper img { width: 100%; height: 270px; object-fit: cover; display: block; transition: transform 0.3s ease; }
    .product-img-wrapper img:hover { transform: scale(1.03); }
    
    .badge-discount { position: absolute; top: 10px; right: 10px; background-color: #e11d48; color: #ffffff; padding: 4px 9px; font-size: 0.78rem; font-weight: 700; border-radius: 2px; z-index: 2; }
    .badge-new { position: absolute; bottom: 10px; right: 10px; background-color: #7c7c7c; color: #ffffff; padding: 3px 10px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; z-index: 2; }
    
    .product-title { font-size: 1.2rem; color: #1f2937; font-weight: 700; margin: 4px 0 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .product-sub { font-size: 0.8rem; color: #6b7280; margin-bottom: 6px; }
    
    .price-offer { color: #e11d48; font-size: 1.25rem; font-weight: 800; margin-right: 8px; }
    .price-regular { text-decoration: line-through; color: #9ca3af; font-size: 0.92rem; }
    
    .sidebar-filter-title { font-size: 1rem; font-weight: 700; letter-spacing: 0.8px; color: #111827; margin-bottom: 12px; text-transform: uppercase; }
    
    .whatsapp-btn { display: block; background-color: #25D366; color: white !important; text-align: center; padding: 14px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1.05rem; margin-top: 12px; }
</style>
''', unsafe_allow_html=True)

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
# 3. Conexión con Google Sheets
# ---------------------------------------------------------
SHEET_ID = "1LGRa-BfRkiRbyqukW0aWWpHJh2tKV_W-IgB0SRbx8N0"
URL_INV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Inventario"
URL_CLI = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Fidelidad_Clientes"
URL_ENV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Costos_Envio"

@st.cache_data(ttl=15)
def cargar_datos(url, tipo="inv"):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if not df.empty: return df
    except Exception: pass
    
    if tipo == "inv":
        return pd.DataFrame([
            {"Modelo": "Tanara Botas Taco Cuadrado", "Categoría": "Botas", "Material": "Cuero Sintético", "Color": "Animal Print", "Precio Regular ($)": 99.99, "Precio Oferta ($)": 99.99, "En Oferta": "No", "Talla 34": 2, "Talla 35": 3, "Talla 36": 5, "Enlace Imagen": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"},
            {"Modelo": "Hey Dude Hudson Lift", "Categoría": "Deportivos", "Material": "Malla", "Color": "Rosa", "Precio Regular ($)": 95.99, "Precio Oferta ($)": 95.99, "En Oferta": "No", "Talla 34": 1, "Talla 35": 2, "Talla 36": 2, "Enlace Imagen": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111"}
        ])
    elif tipo == "envios":
        return pd.DataFrame([
            {"Provincia": "Los Ríos", "Cantón": "Babahoyo", "Costo ($)": 0.00},
            {"Provincia": "Guayas", "Cantón": "Guayaquil", "Costo ($)": 4.50},
            {"Provincia": "Pichincha", "Cantón": "Quito", "Costo ($)": 5.50},
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
    
    pdf.cell(0, 6, limpiar(f"Cliente: {cl['nombres']} (CI: {cl['cedula']})"), ln=True)
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
# 5. Interfaz: Cabecera 
# ---------------------------------------------------------
st.markdown('''
<div class="top-utility-bar">
    <span>🚚 ENVÍOS CONFIGURABLES POR PROVINCIA</span> | 
    <span>📍 BABAHOYO: PAGO CONTRAENTREGA</span> | 
    <span class="top-utility-highlight">⭐ FIDELIDAD: 0959276539</span>
</div>
''', unsafe_allow_html=True)

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
        if st.button("👤 Cuenta", use_container_width=True):
            st.session_state.vista_actual = "LOGIN"
            st.rerun()
    with c2:
        if st.button("ℹ️ Info", use_container_width=True):
            st.session_state.vista_actual = "INFO"
            st.rerun()
    with c3:
        if st.button(f"🛒 ({sum(i['cantidad'] for i in st.session_state.carrito)})", use_container_width=True, type="primary"):
            st.session_state.vista_actual = "CARRITO"
            st.rerun()

st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# VISTA: DETALLE DE PRODUCTO
# ---------------------------------------------------------
if st.session_state.producto_seleccionado:
    prod = st.session_state.producto_seleccionado
    if st.button("⬅️ Volver al catálogo"):
        st.session_state.producto_seleccionado = None
        st.rerun()
        
    c_img, c_det = st.columns([1, 1])
    
    variantes_modelo = df_inv[df_inv["Modelo"] == prod["modelo"]]
    colores_disp = list(variantes_modelo["Color"].dropna().unique())
    if not colores_disp: colores_disp = [prod["color"]]

    with c_det:
        st.markdown(f"<h2>{prod['modelo']}</h2>", unsafe_allow_html=True)
        st.write(f"**Categoría:** {prod['categoria']}")
        
        color_elegido = st.selectbox("Selecciona el Color:", colores_disp, index=colores_disp.index(prod["color"]) if prod["color"] in colores_disp else 0)
        
        fila_color = variantes_modelo[variantes_modelo["Color"] == color_elegido].iloc[0] if not variantes_modelo.empty else pd.Series(prod)
        
        url_img_actual = preparar_url_imagen(fila_color.get("Enlace Imagen", prod["imagen"]))
        p_ofe = limpiar_numero_float(fila_color.get("Precio Oferta ($)", prod["p_ofe"]))
        p_tarjeta = round(p_ofe * 1.06, 2)
        
        st.markdown(f'''
        <div style='margin-bottom:15px;'>
            <div style='font-size:1.2rem; font-weight:bold; color:#1e293b;'>Precio Transferencia / Efectivo: <span style='color:#e11d48;'>${p_ofe:.2f}</span></div>
            <div style='font-size:0.9rem; color:#64748b; margin-top:5px;'>Precio con Tarjeta (PayPhone): ${p_tarjeta:.2f} <span style='font-size:0.75rem;'>(Incluye 6% com. pasarela)</span></div>
        </div>
        ''', unsafe_allow_html=True)
        
        talla_sel = st.selectbox("Selecciona tu Talla:", ["34", "35", "36", "37", "38", "39", "40"])
        
        col_talla_nombre = f"Talla {talla_sel}"
        stock = limpiar_numero_int(fila_color.get(col_talla_nombre, 0), 0) if col_talla_nombre in fila_color else 0
        
        if stock > 0:
            st.markdown("<div class='stock-ok'>✅ En Stock</div>", unsafe_allow_html=True)
            cant = st.number_input("Cantidad", min_value=1, max_value=stock)
            
            if st.button("AÑADIR AL CARRITO", type="primary", use_container_width=True):
                st.session_state.carrito.append({
                    "modelo": prod["modelo"], "categoria": prod["categoria"], "color": color_elegido,
                    "talla": talla_sel, "cantidad": cant, "precio_ofe": p_ofe,
                    "imagen": url_img_actual, "subtotal": p_ofe * cant
                })
                st.toast("¡Añadido al carrito!")
        else:
            st.markdown("<div class='stock-zero'>❌ Agotado en esta talla</div>", unsafe_allow_html=True)
            
        with st.expander("📏 Ver Guía de Tallas"):
            st.markdown('''
            | Talla | Centímetros |
            |-------|-------------|
            | 34    | 22.5 cm     |
            | 35    | 23.0 cm     |
            | 36    | 23.5 cm     |
            | 37    | 24.0 cm     |
            | 38    | 24.5 cm     |
            | 39    | 25.5 cm     |
            | 40    | 26.0 cm     |
            ''')

    with c_img:
        st.image(url_img_actual, use_container_width=True)

# ---------------------------------------------------------
# VISTA: CATÁLOGO PRINCIPAL 
# ---------------------------------------------------------
elif st.session_state.vista_actual == "DETAL":
    
    col_sidebar, col_catalogo = st.columns([1, 3], gap="large")

    with col_sidebar:
        st.markdown('''
        <button style='width:100%; background-color:#c8394a; color:white; border:none; padding:12px; border-radius:4px; font-weight:bold; margin-bottom:10px;'>
            TODAS
        </button>
        <button style='width:100%; background-color:#1a1a1a; color:white; border:none; padding:15px; font-size:1.2rem; font-weight:bold; letter-spacing:1px; margin-bottom:20px;'>
            TODO EL CALZADO
        </button>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-filter-title">FILTROS</div>', unsafe_allow_html=True)
        
        talla_filtro = st.selectbox("Talla", ["Todas", "34", "35", "36", "37", "38", "39", "40"])
        
        categorias_base = ["Todas"] + sorted([str(c) for c in df_inv["Categoría"].dropna().unique()])
        cat_filtro = st.selectbox("Categorías", categorias_base)

    with col_catalogo:
        df_mostrar = df_inv.copy()
        
        if cat_filtro != "Todas": df_mostrar = df_mostrar[df_mostrar["Categoría"].astype(str).str.upper() == cat_filtro.upper()]
        if busqueda: df_mostrar = df_mostrar[df_mostrar["Modelo"].astype(str).str.contains(busqueda, case=False, na=False)]
        
        modelos_unicos = list(df_mostrar["Modelo"].dropna().unique())
        
        if len(modelos_unicos) == 0:
            st.warning("No se encontraron zapatos con estos filtros.")
        else:
            cols_grid = st.columns(2, gap="medium")
            tarjeta_idx = 0
            
            for idx, nombre_modelo in enumerate(modelos_unicos):
                variantes_modelo = df_mostrar[df_mostrar["Modelo"] == nombre_modelo]
                if variantes_modelo.empty: continue
                
                with cols_grid[tarjeta_idx % 2]:
                    with st.container(border=True):
                        f_c = variantes_modelo.iloc[0]
                        cat = f_c.get("Categoría", "")
                        mat = f_c.get("Material", "")
                        col_default = f_c.get("Color", "")
                        
                        st.markdown(f'<div class="product-title">{nombre_modelo}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="product-sub">Categoría: {cat} | Material: {mat}</div>', unsafe_allow_html=True)
                        
                        p_reg = limpiar_numero_float(f_c.get("Precio Regular ($)", 0))
                        p_ofe = limpiar_numero_float(f_c.get("Precio Oferta ($)", 0))
                        oferta_activa = str(f_c.get("En Oferta", "No")).strip().lower() == "si"
                        
                        porcentaje_desc = int(round(((p_reg - p_ofe) / p_reg) * 100)) if (p_reg > p_ofe and p_reg > 0) else 0
                        img = preparar_url_imagen(f_c.get("Enlace Imagen"))
                        
                        etiqueta_html = f'<span class="badge-discount">-{porcentaje_desc}%</span>' if oferta_activa and porcentaje_desc > 0 else ''
                        
                        st.markdown(f'''
                        <div class="product-img-wrapper">
                            {etiqueta_html}
                            <img src="{img}">
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        if st.button("Ver Detalle", key=f"det_{idx}", use_container_width=True):
                            st.session_state.producto_seleccionado = {
                                "modelo": nombre_modelo, "categoria": cat, "color": col_default, 
                                "imagen": img, "p_ofe": p_ofe
                            }
                            st.rerun()

                tarjeta_idx += 1

# ---------------------------------------------------------
# VISTA: CARRITO
# ---------------------------------------------------------
elif st.session_state.vista_actual == "CARRITO":
    st.markdown('<div class="category-banner-black" style="text-align:left;">CARRITO DE COMPRAS</div>', unsafe_allow_html=True)
    if not st.session_state.carrito: st.warning("Tu carrito está vacío.")
    else:
        c_res, c_chk = st.columns([1, 1.2])
        subt = 0.0
        
        with c_res:
            for i, it in enumerate(st.session_state.carrito):
                subt += it["subtotal"]
                with st.container(border=True):
                    st.write(f"**{it['modelo']}** ({it['color']} - Talla {it['talla']})")
                    st.write(f"Cant: {it['cantidad']} x ${it['precio_ofe']:.2f} = **${it['subtotal']:.2f}**")
                    if st.button("Quitar", key=f"q_{i}"):
                        st.session_state.carrito.pop(i)
                        st.rerun()
                        
        with c_chk:
            st.subheader("Datos de Envío y Pago")
            
            with st.form("chk"):
                ced = st.text_input("Cédula")
                nom = st.text_input("Nombres y Apellidos")
                
                st.text("País: Ecuador")
                
                lista_prov = ["Guayas", "Pichincha", "Los Ríos", "Azuay", "Manabí", "El Oro", "Tungurahua"]
                if not df_envios.empty and "Provincia" in df_envios.columns:
                    lista_prov = sorted(list(df_envios["Provincia"].dropna().unique()))
                
                prov = st.selectbox("Provincia", lista_prov)
                
                cantones = ["Seleccione Provincia"]
                if not df_envios.empty and "Cantón" in df_envios.columns:
                    cantones = df_envios[df_envios["Provincia"] == prov]["Cantón"].tolist()
                if not cantones: cantones = ["Cantón Principal"]
                
                canton = st.selectbox("Cantón / Ciudad", cantones)
                dir_ex = st.text_area("Dirección Exacta")
                
                mpago = st.radio("Método de Pago", ["Transferencia", "Tarjeta de Crédito / PayPhone (+6%)", "Efectivo (Solo Babahoyo)"])
                guardar = st.checkbox("Guardar mis datos y participar en el Club de Fidelidad", value=True)
                
                btn = st.form_submit_button("Confirmar Compra", type="primary", use_container_width=True)
                
            if btn:
                if not ced or not nom: st.error("Por favor completa los campos obligatorios.")
                else:
                    costo_env = 5.00
                    if not df_envios.empty:
                        fila_e = df_envios[(df_envios["Provincia"] == prov) & (df_envios["Cantón"] == canton)]
                        if not fila_e.empty: costo_env = limpiar_numero_float(fila_e.iloc[0]["Costo ($)"])
                    
                    tarifa_pp = round(subt * 0.06, 2) if "Tarjeta" in mpago else 0.0
                    tot = round(subt + costo_env + tarifa_pp, 2)
                    cod = f"ORD-{random.randint(1000, 9999)}"
                    
                    st.success(f"¡Orden {cod} generada con éxito!")
                    st.write(f"Subtotal: ${subt:.2f} | Envío ({canton}): ${costo_env:.2f} | Recargo Tarjeta: ${tarifa_pp:.2f}")
                    st.markdown(f"### Total a Pagar: ${tot:.2f}")
                    
                    cli_d = {"cedula": ced, "nombres": nom, "apellidos": "", "celular": "", "provincia": prov, "canton": canton, "direccion": dir_ex, "metodo_pago": mpago}
                    pdf_b = generar_pdf_pedido(cod, cli_d, st.session_state.carrito, costo_env + tarifa_pp, subt, tot)
                    st.download_button("Descargar Nota de Pedido (PDF)", pdf_b, f"{cod}.pdf", "application/pdf")
                    
                    msg = f"Hola, orden *{cod}*\nCliente: {nom}\nEnvío a {prov}, {canton}\nPago: {mpago}\n\n"
                    for it in st.session_state.carrito:
                        msg += f"- {it['cantidad']}x {it['modelo']} ({it['color']} - T{it['talla']}) = ${it['subtotal']:.2f}\n"
                    msg += f"\nTotal: ${tot:.2f}"
                    
                    if "Tarjeta" in mpago: msg += f"\n👉 Solicito Link PayPhone por ${tot:.2f} (Incluye comisiones de pasarela)."
                    st.markdown(f'<a href="https://wa.me/593959276539?text={urllib.parse.quote(msg)}" target="_blank" class="whatsapp-btn">Enviar Pedido a WhatsApp</a>', unsafe_allow_html=True)

# ---------------------------------------------------------
# VISTA: INFO & LOGIN 
# ---------------------------------------------------------
elif st.session_state.vista_actual == "INFO":
    st.markdown('<div class="category-banner-black" style="text-align:left;">INFORMACIÓN Y PAGOS</div>', unsafe_allow_html=True)
    st.write("Aceptamos Transferencias, Depósitos y Pago Contraentrega (solo Babahoyo) sin recargo.")
    st.warning("**Pagos con Tarjeta (PayPhone):** Generan un recargo del **6% (5% + IVA) por procesamiento**.")

elif st.session_state.vista_actual == "LOGIN":
    st.markdown('<div class="category-banner-black" style="text-align:left;">MI CUENTA Y FIDELIDAD</div>', unsafe_allow_html=True)
    st.write("Inicia sesión con tu cédula para ver tus puntos de fidelidad.")
