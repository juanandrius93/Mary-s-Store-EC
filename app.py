import streamlit as st
import pandas as pd

# Configuración de la página con la identidad visual de Babayork Urban / Mary's Store Ec
st.set_page_config(page_title="Babayork Urban & Mary's Store Ec", page_icon="👠", layout="wide")

st.title("👠 Babayork Urban / Mary’s Store Ec - Tienda Online")
st.markdown("---")

# Enlace de conexión directa con tu Google Sheet oficial
SHEET_ID = "1LGRa-BfRkiRbyqukW0aWWpHJh2tKV_W-IgB0SRbx8N0"
sheet_name = "Inventario"
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=10) # Se actualiza casi al instante cada 10 segundos
def cargar_inventario_desde_sheet():
    try:
        df = pd.read_csv(sheet_url)
        # Limpiar posibles espacios en los nombres de las columnas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

df_inventario = cargar_inventario_desde_sheet()

# Menú lateral para navegar entre Módulos
menu = st.sidebar.selectbox("Selecciona el Módulo", ["🛍️ Catálogo (Clientes)", "🔒 Gestión Interna (Administrador & Proveedores)", "🏢 Modo Mayorista"])

if menu == "🛍️ Catálogo (Clientes)":
    st.header("Catálogo Disponible - Envíos a todo el Ecuador")
    
    if df_inventario.empty:
        st.warning("⚠️ No se pudo cargar el inventario. Verifica que tu Google Sheet tenga una pestaña llamada 'Inventario' y permisos públicos de lectura.")
    else:
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            categorias = ["Todos"] + list(df_inventario["Categoría"].dropna().unique()) if "Categoría" in df_inventario.columns else ["Todos"]
            cat_seleccionada = st.selectbox("Filtrar por tipo de zapato:", categorias)
        with col_f2:
            busqueda = st.text_input("Buscar modelo específico:")

        df_filtrado = df_inventario
        if cat_seleccionada != "Todos" and "Categoría" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["Categoría"] == cat_seleccionada]
        if busqueda and "Modelo" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["Modelo"].str.contains(busqueda, case=False, na=False)]

        # Mostrar productos
        for index, row in df_filtrado.iterrows():
            modelo = row.get('Modelo', 'Zapato')
            categoria = row.get('Categoría', 'Calzado')
            st.markdown(f"### {modelo} ({categoria})")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                img_url = row.get('Enlace Imagen')
                if pd.notna(img_url):
                    st.image(str(img_url), width=250)
            with col2:
                precio_oferta = row.get('Precio Oferta ($)', row.get('Precio ($)', 19.99))
                st.markdown(f"**Precio Oferta:** ${precio_oferta}")
                st.write(f"**Material:** {row.get('Material', 'Estándar')} | **Tallas:** {row.get('Tallas', '34-40')}")
                st.write(f"**Colores:** {row.get('Colores Disponibles', 'Varios')}")
                st.write(f"**Estado:** {row.get('Estado', 'Disponible')}")
                
                talla_elegida = st.selectbox(f"Elige talla para {modelo}", ["34", "35", "36", "37", "38", "39", "40"], key=f"talla_{index}")
                color_elegido = st.text_input(f"Escribe el color deseado", key=f"color_{index}")
                
                estado_prod = str(row.get('Estado', 'Disponible')).strip()
                if estado_prod == "Disponible":
                    if st.button(f"🛒 Pedir {modelo}", key=f"btn_{index}"):
                        st.success(f"¡Pedido registrado! Envía este mensaje al WhatsApp **0959276539**: Hola, quiero el modelo {modelo}, Talla {talla_elegida}, Color {color_elegido}.")
                else:
                    st.warning("Producto agotado temporalmente o en preventa.")
            st.markdown("---")

elif menu == "🔒 Gestión Interna (Administrador & Proveedores)":
    st.header("Panel de Control Privado (Inventario y Proveedores)")
    st.warning("Zona exclusiva para el equipo de Mary's Store Ec.")
    
    if not df_inventario.empty:
        st.subheader("Inventario en tiempo real desde Google Sheets")
        st.dataframe(df_inventario)
        st.info("💡 Cada cambio que tus trabajadores hagan en el Google Sheet (cambiar stock, precios o agregar modelos y fotos) se reflejará automáticamente en la página web.")

elif menu == "🏢 Modo Mayorista":
    st.header("Zona de Ventas al Por Mayor (Activada por Temporada)")
    st.info("Aquí los distribuidores autorizados pueden visualizar precios especiales por volumen (Mínimo 6 pares).")
    
    if not df_inventario.empty:
        st.dataframe(df_inventario)
    st.markdown("### Requisitos Mayoristas")
    st.write("- Compra mínima: 6 pares surtidos.")
    st.write("- Descuento especial aplicado por temporada.")
