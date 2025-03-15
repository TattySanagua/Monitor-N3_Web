from django.shortcuts import render
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ..embalse.models import Embalse
from ..medicion.models import Medicion
from ..instrumento.models import Instrumento

def calculo_estadistico(parametro):
    if parametro == 'nivel_embalse':
        embalse_data = Embalse.objects.values("fecha", "nivel_embalse")
        df = pd.DataFrame(list(embalse_data))
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha")

        nombre_columna_valor = "nivel_embalse"
        titulo_histograma = "Distribución del Nivel de Embalse"
        titulo_linea = "Evolución del Nivel de Embalse"
        eje_y_titulo = "Nivel (msnm)"

        #Estadísticas generales
        estadisticas = calcular_estadisticas(df, nombre_columna_valor)

        #Histograma general
        hist_html = generar_histograma(df, nombre_columna_valor, titulo_histograma)

        #Gráfico de evolución
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df["fecha"], y=df[nombre_columna_valor],
                                      mode="lines+markers", name="Nivel Embalse"))
        fig_line.update_layout(title=titulo_linea, xaxis_title="Fecha", yaxis_title=eje_y_titulo,
                               template="plotly_white")

        return estadisticas, [hist_html], fig_line.to_html(full_html=False)

    elif parametro == 'nivel_piezometrico':
        mediciones = Medicion.objects.filter(id_instrumento__id_tipo__nombre_tipo='PIEZÓMETRO')
        df = pd.DataFrame(list(mediciones.values('fecha', 'valor', 'id_instrumento__nombre')))

        if df.empty:
            return {}, [], ""

        df = df.rename(columns={'valor': 'nivel_piezometrico', 'id_instrumento__nombre': 'nombre_instrumento'})
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha")

        nombre_columna_valor = "nivel_piezometrico"
        eje_y_titulo = "Nivel (msnm)"

        #Estadísticas para cada piezómetro
        estadisticas_todos = {}
        histogramas_individuales = []

        for instrumento in df["nombre_instrumento"].unique():
            df_instrumento = df[df["nombre_instrumento"] == instrumento].copy()
            estadisticas_todos[instrumento] = calcular_estadisticas(df_instrumento, nombre_columna_valor)

            #Histogramas individuales
            titulo_histograma = f"Distribución del Nivel Piezométrico - {instrumento}"
            hist_individual = generar_histograma(df_instrumento, nombre_columna_valor, titulo_histograma)
            histogramas_individuales.append(hist_individual)

        #Histograma General
        titulo_histograma_general = "Distribución del Nivel Piezométrico - Todos los Instrumentos"
        hist_general = generar_histograma(df, nombre_columna_valor, titulo_histograma_general)

        #Gráfico de evolución
        titulo_linea = "Evolución del Nivel Piezométrico - Todos los Instrumentos"
        fig_line = go.Figure()

        for instrumento in df["nombre_instrumento"].unique():
            df_instrumento = df[df["nombre_instrumento"] == instrumento].copy()
            fig_line.add_trace(go.Scatter(x=df_instrumento["fecha"], y=df_instrumento[nombre_columna_valor],
                                          mode="lines+markers", name=instrumento))

        fig_line.update_layout(title=titulo_linea, xaxis_title="Fecha", yaxis_title=eje_y_titulo,
                               template="plotly_white")

        return estadisticas_todos, [hist_general] + histogramas_individuales, fig_line.to_html(full_html=False)

    elif parametro == 'nivel_freatico':
        mediciones = Medicion.objects.filter(id_instrumento__id_tipo__nombre_tipo='FREATÍMETRO')
        df = pd.DataFrame(list(mediciones.values('fecha', 'valor', 'id_instrumento__nombre')))

        if df.empty:
            return {}, [], ""

        df = df.rename(columns={'valor': 'nivel_freatico', 'id_instrumento__nombre': 'nombre_instrumento'})
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha")

        nombre_columna_valor = "nivel_freatico"
        eje_y_titulo = "Nivel (msnm)"

        #Estadísticas para cada freatimetro
        estadisticas_todos = {}
        histogramas_individuales = []

        for instrumento in df["nombre_instrumento"].unique():
            df_instrumento = df[df["nombre_instrumento"] == instrumento].copy()
            estadisticas_todos[instrumento] = calcular_estadisticas(df_instrumento, nombre_columna_valor)

            #Histogramas individuales
            titulo_histograma = f"Distribución del Nivel Freático - {instrumento}"
            hist_individual = generar_histograma(df_instrumento, nombre_columna_valor, titulo_histograma)
            histogramas_individuales.append(hist_individual)

        #Histograma General
        titulo_histograma_general = "Distribución del Nivel Freático - Todos los Instrumentos"
        hist_general = generar_histograma(df, nombre_columna_valor, titulo_histograma_general)

        #Gráfico de evolución
        titulo_linea = "Evolución del Nivel Freático - Todos los Instrumentos"
        fig_line = go.Figure()

        for instrumento in df["nombre_instrumento"].unique():
            df_instrumento = df[df["nombre_instrumento"] == instrumento].copy()
            fig_line.add_trace(go.Scatter(x=df_instrumento["fecha"], y=df_instrumento[nombre_columna_valor],
                                          mode="lines+markers", name=instrumento))

        fig_line.update_layout(title=titulo_linea, xaxis_title="Fecha", yaxis_title=eje_y_titulo,
                               template="plotly_white")

        return estadisticas_todos, [hist_general] + histogramas_individuales, fig_line.to_html(full_html=False)

    elif parametro == 'caudal':
        mediciones = Medicion.objects.filter(id_instrumento__id_tipo__nombre_tipo__contains='AFORADOR')
        df = pd.DataFrame(list(mediciones.values('fecha', 'valor', 'id_instrumento__nombre')))

        if df.empty:
            return {}, [], ""

        df = df.rename(columns={'valor': 'caudal', 'id_instrumento__nombre': 'nombre_aforador'})
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.sort_values("fecha")

        nombre_columna_valor = "caudal"
        eje_y_titulo = "Caudal (m³/s)"

        #Estadísticas para cada aforador
        estadisticas_todos = {}
        histogramas_individuales = []

        for aforador in df["nombre_aforador"].unique():
            df_aforador = df[df["nombre_aforador"] == aforador].copy()
            estadisticas_todos[aforador] = calcular_estadisticas(df_aforador, nombre_columna_valor)

            #Histogramas individuales
            titulo_histograma = f"Distribución del Caudal - {aforador}"
            hist_individual = generar_histograma(df_aforador, nombre_columna_valor, titulo_histograma)
            histogramas_individuales.append(hist_individual)

        #Histograma General
        titulo_histograma_general = "Distribución del Caudal - Todos los Aforadores"
        hist_general = generar_histograma(df, nombre_columna_valor, titulo_histograma_general)

        #Gráfico de evolución
        titulo_linea = "Evolución del Caudal - Todos los Aforadores"
        fig_line = go.Figure()

        for aforador in df["nombre_aforador"].unique():
            df_aforador = df[df["nombre_aforador"] == aforador].copy()
            fig_line.add_trace(go.Scatter(x=df_aforador["fecha"], y=df_aforador[nombre_columna_valor],
                                          mode="lines+markers", name=aforador))

        fig_line.update_layout(title=titulo_linea, xaxis_title="Fecha", yaxis_title=eje_y_titulo,
                               template="plotly_white")

        return estadisticas_todos, [hist_general] + histogramas_individuales, fig_line.to_html(full_html=False)

    else:
        return {}, [], ""

def calcular_estadisticas(df, columna_valor):
        df[columna_valor] = df[columna_valor].astype(float)
        return {
            "media": df[columna_valor].mean(),
            "mediana": df[columna_valor].median(),
            "moda": df[columna_valor].mode().tolist(),
            "maximo": df[columna_valor].max(),
            "minimo": df[columna_valor].min(),
            "desviacion_estandar": df[columna_valor].std(),
            "datos_faltantes": df[columna_valor].isna().sum(),
            "fuera_de_rango": df[(df[columna_valor] < df[columna_valor].quantile(0.05)) |
                                 (df[columna_valor] > df[columna_valor].quantile(0.95))].shape[0]
        }

def generar_histograma(df, columna_valor, titulo):
        fig_hist = px.histogram(df, x=columna_valor, nbins=30, title=titulo)
        fig_hist.update_layout(template="plotly_white")
        return fig_hist.to_html(full_html=False)

def resumen_estadistico(request):
    parametro = request.GET.get('parametro', 'nivel_embalse')

    estadisticas, histogramas, line_html = calculo_estadistico(parametro)

    return render(request, "resumen_estadistico.html", {
        "estadisticas": estadisticas,
        "grafico_histograma": histogramas,
        "grafico_linea": line_html,
        "parametro_seleccionado": parametro,
    })