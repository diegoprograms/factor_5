import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Flexibilidad Curricular",
    layout="wide"
)

st.title("Herramienta de Flexibilidad Curricular")
st.markdown("""
Esta herramienta permite cargar, visualizar y analizar rutas de formación alternativas
asociadas a estrategias de flexibilidad curricular.
""")

archivo = st.file_uploader(
    "Suba un archivo Excel o CSV",
    type=["xlsx", "csv"]
)

if archivo is not None:

    if archivo.name.endswith(".xlsx"):
        df = pd.read_excel(archivo)
    else:
        df = pd.read_csv(archivo)

    # ==============================
    # ANONIMIZACIÓN DE DATOS
    # ==============================

    columnas_sensibles = [
        "Nombre",
        "Nombres",
        "Apellidos",
        "Documento",
        "Cédula",
        "Cedula",
        "Correo",
        "Email",
        "Telefono",
        "Teléfono",
        "Celular",
        "Dirección",
        "Direccion"
    ]

    df = df.drop(
        columns=[col for col in columnas_sensibles if col in df.columns],
        errors="ignore"
    )

    df["ID_anonimo"] = [
        "EST_" + str(i).zfill(4)
        for i in range(1, len(df) + 1)
    ]

    st.subheader("Vista inicial de los datos anonimizados")
    st.dataframe(df)

    st.sidebar.header("Filtros")

    programa = st.sidebar.selectbox(
        "Programa",
        ["Todos"] + sorted(df["Programa"].dropna().unique().tolist())
    )

    cohorte = st.sidebar.selectbox(
        "Cohorte",
        ["Todos"] + sorted(df["Cohorte"].dropna().astype(str).unique().tolist())
    )

    tipo_ruta = st.sidebar.selectbox(
        "Tipo de ruta",
        ["Todos"] + sorted(df["Tipo_ruta"].dropna().unique().tolist())
    )

    estado = st.sidebar.selectbox(
        "Estado",
        ["Todos"] + sorted(df["Estado"].dropna().unique().tolist())
    )

    datos = df.copy()

    if programa != "Todos":
        datos = datos[datos["Programa"] == programa]

    if cohorte != "Todos":
        datos = datos[datos["Cohorte"].astype(str) == cohorte]

    if tipo_ruta != "Todos":
        datos = datos[datos["Tipo_ruta"] == tipo_ruta]

    if estado != "Todos":
        datos = datos[datos["Estado"] == estado]

    st.subheader("Indicadores")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Registros", len(datos))
    col2.metric("Estudiantes únicos", datos["ID_anonimo"].nunique())
    col3.metric("Promedio créditos", round(datos["Creditos"].mean(), 2) if len(datos) > 0 else 0)
    col4.metric("Total créditos", int(datos["Creditos"].sum()) if len(datos) > 0 else 0)

    st.subheader("Datos filtrados")
    st.dataframe(datos)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        conteo_rutas = datos["Tipo_ruta"].value_counts().reset_index()
        conteo_rutas.columns = ["Tipo_ruta", "Cantidad"]

        fig1 = px.bar(
            conteo_rutas,
            x="Tipo_ruta",
            y="Cantidad",
            title="Cantidad por tipo de ruta"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        fig2 = px.pie(
            datos,
            names="Estado",
            title="Distribución por estado"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Resumen por cohorte")

    resumen_cohorte = datos.groupby("Cohorte").agg(
        estudiantes=("ID_anonimo", "nunique"),
        registros=("Tipo_ruta", "count"),
        creditos_promedio=("Creditos", "mean"),
        total_creditos=("Creditos", "sum")
    ).reset_index()

    st.dataframe(resumen_cohorte)

else:
    st.info("Suba un archivo para iniciar el análisis.")