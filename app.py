import streamlit as st
import pandas as pd

# Configuración de la página con la identidad visual de Babayork Urban / Mary's Store Ec
st.set_page_config(page_title="Babayork Urban & Mary's Store Ec", page_icon="👠", layout="wide")

st.title("👠 Babayork Urban / Mary’s Store Ec - Tienda Online")
st.markdown("---")

# Enlace de tu Google Sheet de Inventario en el Drive
SHEET_ID = "1P3GVavBtKvsrPVKJbq5IUB6SUfVzTbN9"
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
            categorias = ["Todos"] + list(df_inventario["Categoría"].unique())
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
            st.markdown(f"### {row['Modelo']} ({row['Categoría']})")
            col1, col2 = st.columns([1, 2])
            with col1:
                if pd.notna(row.get("Enlace Imagen")):
                    st.image(str(row["Enlace Imagen"]), width=250)
            with col2:
                st.markdown(f"**Precio Oferta:** ${row['Precio Oferta ($)']}")
                st.write(f"**Material:** {row['Material']} | **Tallas:** {row['Tallas']}")
                st.write(f"**Colores:** {row['Colores Disponibles']}")
                st.write(f"**Estado:** {row['Estado']}")
                
                talla_elegida = st.selectbox(f"Elige talla para {row['Modelo']}", ["34", "35", "36", "37", "38", "39", "40"], key=f"talla_{row['ID']}")
                color_elegido = st.text_input(f"Escribe el color deseado", key=f"color_{row['ID']}")
                
                if str(row["Estado"]).strip() == "Disponible":
                    if st.button(f"🛒 Pedir {row['Modelo']}", key=f"btn_{row['ID']}"):
                        st.success(f"¡Pedido registrado! Envía este mensaje al WhatsApp **0959276539**: Hola, quiero el modelo {row['Modelo']}, Talla {talla_elegida}, Color {color_elegido}.")
                else:
                    st.warning("Producto agotado temporalmente o en preventa con proveedor.")
            st.markdown("---")

elif menu == "🔒 Gestión Interna (Administrador & Proveedores)":
    st.header("Panel de Control Privado (Inventario y Proveedores)")
    st.warning("Zona exclusiva para el administrador de Mary's Store Ec.")
    
    if not df_inventario.empty:
        st.subheader("Inventario Actual sincronizado con Google Sheets")
        st.dataframe(df_inventario[["ID", "Modelo", "Categoría", "Stock", "Estado", "Proveedor"]])
        st.info("💡 A partir de ahora, cada vez que actualices precios, stock o agregues modelos en tu Google Sheet, la página web reflejará los cambios automáticamente.")

elif menu == "🏢 Modo Mayorista":
    st.header("Zona de Ventas al Por Mayor (Activada por Temporada)")
    st.info("Aquí los distribuidores autorizados pueden visualizar precios especiales por volumen (Mínimo 6 pares).")
    
    if not df_inventario.empty:
        st.dataframe(df_inventario[["Modelo", "Material", "Precio Oferta ($)", "Proveedor"]])
    st.markdown("### Requisitos Mayoristas")
    st.write("- Compra mínima: 6 pares surtidos.")
    st.write("- Descuento especial aplicado por temporada.")
