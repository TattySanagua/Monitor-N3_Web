import base64
import io

import numpy as np
from django.shortcuts import render
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.statespace.sarimax import SARIMAX
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression
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
            "media": round(df[columna_valor].mean(), 2),
            "mediana": round(df[columna_valor].median(), 2),
            "moda": [round(x, 2) for x in df[columna_valor].mode().tolist()],
            "maximo": round(df[columna_valor].max(), 2),
            "minimo": round(df[columna_valor].min(), 2),
            "desviacion_estandar": round(df[columna_valor].std(), 2),
            "datos_faltantes": df[columna_valor].isna().sum(),
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

def predicciones(request):
    # 1. Obtener el período de la media móvil desde el formulario (por defecto, 12 meses)
    periodo = int(request.GET.get("periodo", 12))

    # 2. Obtener datos históricos del nivel de embalse
    embalse_data = Embalse.objects.values("fecha", "nivel_embalse")
    df = pd.DataFrame(list(embalse_data))
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha")
    df = df.set_index("fecha").sort_index()
    df = df[df.index >= "2016-01-01"]

    # Convertir a tipo numérico y manejar valores NaN
    df["nivel_embalse"] = pd.to_numeric(df["nivel_embalse"], errors="coerce")
    df.dropna(subset=["nivel_embalse"], inplace=True)

    # 3. Calcular media móvil con el período seleccionado
    df["media_movil"] = df["nivel_embalse"].rolling(window=periodo, min_periods=1).mean()

    # 4. Prueba de estacionariedad (Dickey-Fuller ADF)
    adf_test = adfuller(df["nivel_embalse"])
    estacionaria = "Sí" if adf_test[1] < 0.05 else "No"  # p-valor < 0.05 significa que es estacionaria

    # 5. Descomposición de la serie en tendencia, estacionalidad e irregularidad
    descomposicion = seasonal_decompose(df["nivel_embalse"], model="additive", period=12)

    # 6. Aplicar Modelos AR, MA y ARMA

    # 6.1 Correlograma (ACF y PACF)
    fig_acf, ax_acf = plt.subplots()
    plot_acf(df["nivel_embalse"], ax=ax_acf, lags=40)  # Gráfico ACF

    fig_pacf, ax_pacf = plt.subplots()
    plot_pacf(df["nivel_embalse"], ax=ax_pacf, lags=40)  # Gráfico PACF

    # Convertir los gráficos de Matplotlib a HTML con Plotly
    def matplotlib_to_plotly(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{encoded}" style="width:100%;">'

    grafico_acf = matplotlib_to_plotly(fig_acf)
    grafico_pacf = matplotlib_to_plotly(fig_pacf)

    # a) Modelo AR (Autorregresivo)
    modelo_ar = SARIMAX(df["nivel_embalse"], order=(1, 0, 0), enforce_stationarity=False, enforce_invertibility=False)  # AR(2)
    resultado_ar = modelo_ar.fit()
    df["pred_AR"] = resultado_ar.fittedvalues

    # b) Modelo MA (Media Móvil)
    modelo_ma = SARIMAX(df["nivel_embalse"], order=(0, 0, 2), enforce_stationarity=False, enforce_invertibility=False)  # MA(2)
    resultado_ma = modelo_ma.fit()
    df["pred_MA"] = resultado_ma.fittedvalues

    # c) Modelo ARMA (Autorregresivo + Media Móvil)
    modelo_arma = SARIMAX(df["nivel_embalse"], order=(2, 0, 2), enforce_stationarity=False, enforce_invertibility=False)  # ARMA(2,2)
    resultado_arma = modelo_arma.fit()
    df["pred_ARMA"] = resultado_arma.fittedvalues

    # Definir el número de pasos de predicción (por ejemplo, 365 días)
    steps_a_predecir = 1095

    # Predecir con cada modelo
    pred_ar = resultado_ar.get_forecast(steps=steps_a_predecir).predicted_mean
    pred_ma = resultado_ma.get_forecast(steps=steps_a_predecir).predicted_mean
    pred_arma = resultado_arma.get_forecast(steps=steps_a_predecir).predicted_mean

    # Crear rango de fechas futuras
    fecha_final = df.index[-1]
    fechas_futuras = pd.date_range(start=fecha_final, periods=steps_a_predecir + 1, freq="D")[1:]

    # 7. Crear gráficos con Plotly

    # a) Evolución del nivel de embalse con media móvil
    fig_evolucion = go.Figure()
    fig_evolucion.add_trace(go.Scatter(x=df.index, y=df["nivel_embalse"], mode="lines", name="Nivel Embalse"))
    fig_evolucion.add_trace(
        go.Scatter(x=df.index, y=df["media_movil"], mode="lines", name=f"Media Móvil ({periodo} meses)",
                   line=dict(dash="dot", color="red")))

    fig_evolucion.update_layout(title="Evolución del Nivel de Embalse con Media Móvil",
                                xaxis_title="Fecha", yaxis_title="Nivel (msnm)",
                                template="plotly_white")

    # b) Descomposición de la serie de tiempo
    fig_descomposicion = go.Figure()
    fig_descomposicion.add_trace(go.Scatter(x=df.index, y=descomposicion.trend, mode="lines", name="Tendencia"))
    fig_descomposicion.add_trace(go.Scatter(x=df.index, y=descomposicion.seasonal, mode="lines", name="Estacionalidad"))
    fig_descomposicion.add_trace(go.Scatter(x=df.index, y=descomposicion.resid, mode="lines", name="Irregularidad"))
    fig_descomposicion.update_layout(title="Descomposición de la Serie de Tiempo",
                                     xaxis_title="Fecha", yaxis_title="Valores",
                                     template="plotly_white")

    # c) Predicciones con modelos AR, MA y ARMA
    fig_ajuste = go.Figure()
    fig_ajuste.add_trace(go.Scatter(x=df.index, y=df["nivel_embalse"], mode="lines", name="Nivel Embalse"))
    fig_ajuste.add_trace(
        go.Scatter(x=df.index, y=df["pred_AR"], mode="lines", name="Modelo AR", line=dict(dash="dot", color="blue")))
    # fig_ajuste.add_trace(
    #     go.Scatter(x=df.index, y=df["pred_MA"], mode="lines", name="Modelo MA", line=dict(dash="dot", color="green")))
    fig_ajuste.add_trace(go.Scatter(x=df.index, y=df["pred_ARMA"], mode="lines", name="Modelo ARMA",
                                    line=dict(dash="dot", color="purple")))
    fig_ajuste.update_layout(title="Ajuste del Modelo AR, MA y ARMA", xaxis_title="Fecha", yaxis_title="Nivel (msnm)")

    # Gráfico de predicciones futuras
    fig_futuro = go.Figure()
    fig_futuro.add_trace(
        go.Scatter(x=fechas_futuras, y=pred_ar, mode="lines", name="Pred. AR", line=dict(color="blue", dash="dash")))
    # fig_futuro.add_trace(
    #     go.Scatter(x=fechas_futuras, y=pred_ma, mode="lines", name="Pred. MA", line=dict(color="green", dash="dot")))
    fig_futuro.add_trace(go.Scatter(x=fechas_futuras, y=pred_arma, mode="lines", name="Pred. ARMA",
                                    line=dict(color="purple", dash="dashdot")))
    fig_futuro.update_layout(title="Predicciones Futuras", xaxis_title="Fecha", yaxis_title="Nivel (msnm)")

    return render(request, "predicciones_modelos.html", {
        "grafico_evolucion": fig_evolucion.to_html(full_html=False),
        "grafico_descomposicion": fig_descomposicion.to_html(full_html=False),
        "grafico_predicciones": fig_ajuste.to_html(full_html=False),
        "grafico_futuro": fig_futuro.to_html(full_html=False),
        "grafico_acf": grafico_acf,  # 🔹 ACF
        "grafico_pacf": grafico_pacf,  # 🔹 PACF
        "es_estacionaria": estacionaria,
        "p_valor": adf_test[1],
        "periodo_seleccionado": periodo,
    })

def correlaciones(request):
    # Obtener datos históricos del nivel de embalse
    embalse_data = Embalse.objects.values("fecha", "nivel_embalse")

    # Obtener datos de medición para piezómetros y freatímetros
    medicion_data = Medicion.objects.filter(
        id_instrumento__id_tipo__nombre_tipo__in=['PIEZÓMETRO', 'FREATÍMETRO']
    ).values("fecha", "valor", "id_instrumento__nombre", "id_instrumento__id_tipo__nombre_tipo")

    # Convertir a DataFrame
    df_embalse = pd.DataFrame(list(embalse_data))
    df_medicion = pd.DataFrame(list(medicion_data))

    # Convertir fechas y fusionar datasets
    df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
    df_medicion["fecha"] = pd.to_datetime(df_medicion["fecha"])
    df = pd.merge(df_embalse, df_medicion, on="fecha", how="inner")

    # Renombrar columnas
    df.rename(columns={"nivel_embalse": "Embalse", "valor": "Nivel", "id_instrumento__nombre": "Instrumento",
                       "id_instrumento__id_tipo__nombre_tipo": "Tipo"}, inplace=True)
    print(df)

    # Convertir valores a numéricos y eliminar NaN
    df["Embalse"] = pd.to_numeric(df["Embalse"], errors="coerce")
    df["Nivel"] = pd.to_numeric(df["Nivel"], errors="coerce")
    df.dropna(subset=["Embalse", "Nivel"], inplace=True)

    # Eliminar filas con valores nulos
    df.dropna(subset=["Embalse", "Nivel"], inplace=True)

    # Listas de instrumentos
    piezometros = ["L3-PC1", "L3-PC2", "L3-PC3", "L3-PC4", "L3-PC5", "L3-PC6", "L3-PC7"]
    freatimetro = ["L3-F1"]
    grupos = {
        "Grupo 1 (F1-PC2-PC3-PC4)": ["L3-F1", "L3-PC2", "L3-PC3", "L3-PC4"],
        "Grupo 2 (PC1-PC5-PC6)": ["L3-PC1", "L3-PC5", "L3-PC6"]
    }

    # Diccionarios para guardar resultados
    correlaciones = []
    graficos_dispersion = {}


    # Función para crear gráfico de dispersión y calcular regresión
    def crear_grafico(x, y, nombre):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="Datos"))

        # 🔸 Calcular regresión lineal si la relación es fuerte (> 0.7)
        pearson_corr, _ = pearsonr(x, y)
        spearman_corr, _ = spearmanr(x, y)
        relacion_lineal = "Sí" if abs(pearson_corr) > 0.7 else "No"

        if relacion_lineal == "Sí":
            modelo = LinearRegression()
            x_vals = np.array(x).reshape(-1, 1)
            modelo.fit(x_vals, y)
            y_pred = modelo.predict(x_vals)
            fig.add_trace(go.Scatter(x=x, y=y_pred, mode="lines", name="Regresión", line=dict(color="red")))

        fig.update_layout(title=f"Relación Nivel de Embalse vs {nombre}",
                          xaxis_title="Nivel de Embalse (msnm)",
                          yaxis_title=f"{nombre} (m)",
                          template="plotly_white")
        return fig, pearson_corr, spearman_corr, relacion_lineal

    # Calcular correlaciones para cada piezómetro individualmente
    for pz in piezometros:
        df_pz = df[df["Instrumento"] == pz]
        if not df_pz.empty:
            fig, pearson, spearman, lineal = crear_grafico(df_pz["Embalse"], df_pz["Nivel"], pz)
            graficos_dispersion[pz] = fig.to_html(full_html=False)
            correlaciones.append((pz, pearson, spearman, lineal))

    # Calcular correlación para el freatímetro F1
    df_f1 = df[df["Instrumento"] == "L3-F1"]
    if not df_f1.empty:
        fig, pearson, spearman, lineal = crear_grafico(df_f1["Embalse"], df_f1["Nivel"], "Freatímetro F1")
        graficos_dispersion["L3-F1"] = fig.to_html(full_html=False)
        correlaciones.append(("L3-F1", pearson, spearman, lineal))

    # Calcular correlaciones por grupos
    for nombre_grupo, instrumentos in grupos.items():
        df_grupo = df[df["Instrumento"].isin(instrumentos)]
        if not df_grupo.empty:
            fig, pearson, spearman, lineal = crear_grafico(df_grupo["Embalse"], df_grupo["Nivel"], nombre_grupo)
            graficos_dispersion[nombre_grupo] = fig.to_html(full_html=False)
            correlaciones.append((nombre_grupo, pearson, spearman, lineal))

            # Renderizar la plantilla con los gráficos y resultados

    return render(request, "correlaciones.html", {
                "graficos_dispersion": graficos_dispersion,
                "correlaciones": correlaciones
            })
