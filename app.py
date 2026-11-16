import streamlit as st
import pandas as pd

# Configuración de la página con la identidad visual de Babayork Urban / Mary's Store Ec
st.set_page_config(page_title="Babayork Urban & Mary's Store Ec", page_icon="👠", layout="wide")

st.title("👠 Babayork Urban / Mary’s Store Ec - Tienda Online")
st.markdown("---")

# Enlace oficial de tu Google Sheet de Inventario en el Drive
SHEET_ID = "1LGRa-BfRkiRbyqukW0aWWpHJh2tKV_W-IgB0SRbx8N0"
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=60)
def cargar_inventario_desde_drive():
    try:
        df = pd.read_csv(sheet_url)
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

df_inventario = cargar_inventario_desde_drive()

# Menú lateral para navegar entre Cliente y Administrador
menu = st.sidebar.selectbox("Selecciona el Módulo", ["🛍️ Catálogo (Clientes)", "🔒 Gestión Interna (Administrador & Proveedores)", "🏢 Modo Mayorista"])

if menu == "🛍️ Catálogo (Clientes)":
    st.header("Catálogo Disponible - Envíos a todo el Ecuador")
    
    if df_inventario.empty:
        st.warning("Cargando inventario o verifica que tu Google Sheet tenga permisos públicos de lectura.")
    else:
        # Filtro por categoría y búsqueda
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            categorias = ["Todos"] + list(df_inventario["Categoría"].unique()) if "Categoría" in df_inventario.columns else ["Todos"]
            cat_seleccionada = st.selectbox("Filtrar por tipo de zapato:", categorias)
        with col_f2:
            busqueda = st.text_input("Buscar modelo específico:")

        df_filtrado = df_inventario
        if cat_seleccionada != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Categoría"] == cat_seleccionada]
        if busqueda:
            df_filtrado = df_filtrado[df_filtrado["Modelo"].str.contains(busqueda, case=False, na=False)]

        # Mostrar productos en una cuadrícula bonita
        for index, row in df_filtrado.iterrows():
            st.markdown(f"### {row.get('Modelo', 'Zapato')} ({row.get('Categoría', 'Calzado')})")
            col1, col2 = st.columns([1, 2])
            with col1:
                if pd.notna(row.get("Enlace Imagen")):
                    st.image(str(row["Enlace Imagen"]), width=250)
            with col2:
                precio_oferta = row.get('Precio Oferta ($)', row.get('Precio ($)', 19.99))
                st.markdown(f"**Precio Oferta:** ${precio_oferta}")
                st.write(f"**Material:** {row.get('Material', 'Estándar')} | **Tallas:** {row.get('Tallas', '34-40')}")
                st.write(f"**Colores:** {row.get('Colores Disponibles', 'Varios')}")
                st.write(f"**Estado:** {row.get('Estado', 'Disponible')}")
                
                talla_elegida = st.selectbox(f"Elige talla para {row.get('Modelo', 'Zapato')}", ["34", "35", "36", "37", "38", "39", "40"], key=f"talla_{index}")
                color_elegido = st.text_input(f"Escribe el color deseado", key=f"color_{index}")
                
                if str(row.get("Estado", "Disponible")).strip() == "Disponible":
                    if st.button(f"🛒 Pedir {row.get('Modelo', 'Zapato')}", key=f"btn_{index}"):
                        st.success(f"¡Pedido registrado! Envía este mensaje al WhatsApp **0959276539**: Hola, quiero el modelo {row.get('Modelo')}, Talla {talla_elegida}, Color {color_elegido}.")
                else:
                    st.warning("Producto agotado temporalmente o en preventa con proveedor.")
            st.markdown("---")

elif menu == "🔒 Gestión Interna (Administrador & Proveedores)":
    st.header("Panel de Control Privado (Inventario y Proveedores)")
    st.warning("Zona exclusiva para el administrador de Mary's Store Ec.")
    
    if not df_inventario.empty:
        st.subheader("Inventario Actual sincronizado con Google Sheets")
        st.dataframe(df_inventario)
        st.info("💡 A partir de ahora, cada vez que actualices precios, stock o agregues modelos en tu Google Sheet, la página web reflejará los cambios automáticamente.")

elif menu == "🏢 Modo Mayorista":
    st.header("Zona de Ventas al Por Mayor (Activada por Temporada)")
    st.info("Aquí los distribuidores autorizados pueden visualizar precios especiales por volumen (Mínimo 6 pares).")
    
    if not df_inventario.empty:
        st.dataframe(df_inventario)
    st.markdown("### Requisitos Mayoristas")
    st.write("- Compra mínima: 6 pares surtidos.")
    st.write("- Descuento especial aplicado por temporada.")
