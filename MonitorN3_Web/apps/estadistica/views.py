import base64
import io
import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ..embalse.models import Embalse
from ..medicion.models import Medicion
from ..instrumento.models import Instrumento, Tipo


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

@login_required(login_url='/login/')
def resumen_estadistico(request):
    parametro = request.GET.get('parametro', 'nivel_embalse')

    estadisticas, histogramas, line_html = calculo_estadistico(parametro)

    return render(request, "resumen_estadistico.html", {
        "estadisticas": estadisticas,
        "grafico_histograma": histogramas,
        "grafico_linea": line_html,
        "parametro_seleccionado": parametro,
    })


def mostrar_instrumentos(request):
    """Renderiza el template con la lista de instrumentos activos."""
    if request.method == "GET":
        instrumentos = Instrumento.objects.filter(activo=True).values("nombre")
        return render(request, "predicciones_modelos.html", {"instrumentos": instrumentos})

@login_required(login_url='/login/')
def predicciones(request):
    context = {}
    instrumentos_activos = Instrumento.objects.filter(activo=True)
    context['instrumentos_activos'] = instrumentos_activos

    if request.method == 'POST':

        nombre_instrumento = request.POST.get('instrumento')
        fechas_supuestas = request.POST.getlist('fecha_supuesta[]')
        niveles_embalse_supuestos = request.POST.getlist('nivel_embalse_supuesto[]')

        instrumento = get_object_or_404(Instrumento, nombre=nombre_instrumento)

        C12 = float(request.POST.get('C12', 110))  # Valor por defecto 110
        C13 = float(request.POST.get('C13', 18))  # Valor por defecto 18
        C14 = float(request.POST.get('C14', 1))  # Valor por defecto 1

        try:
            # Obtener el tipo de medición
            tipo_instrumento = instrumento.id_tipo
            tipo_medicion = tipo_instrumento.tipo_medicion
            context['tipo_medicion'] = tipo_medicion

            # Obtener las mediciones para el instrumento
            mediciones = Medicion.objects.filter(id_instrumento_id=instrumento.id).order_by('fecha')
            df_mediciones = pd.DataFrame(list(mediciones.values()))

            # Obtener los niveles del embalse
            fechas_mediciones = df_mediciones['fecha'].tolist()
            embalses = Embalse.objects.filter(fecha__in=fechas_mediciones)
            df_embalses = pd.DataFrame(list(embalses.values()))

            # Combinar los DataFrames usando merge (join)
            df_combinado = pd.merge(df_mediciones, df_embalses, left_on='fecha', right_on='fecha', how='left')

            # Asegurarse de que la columna 'fecha' sea de tipo datetime de Pandas
            df_combinado['fecha'] = pd.to_datetime(df_combinado['fecha'])

            # --- Cálculos Estadísticos ---
            df_calculos = df_combinado[['fecha', 'nivel_embalse', 'valor']].copy()

            # Convertir 'nivel_embalse' a float
            df_calculos['nivel_embalse'] = df_calculos['nivel_embalse'].apply(
                lambda x: float(x) if isinstance(x, Decimal) else float(x))

            nivel_embalse_max = float(df_calculos['nivel_embalse'].max())
            nivel_embalse_min = float(df_calculos['nivel_embalse'].min())

            df_calculos['A'] = df_calculos['fecha'].dt.year - 1900

            def fecha_juliana(fecha):
                año = fecha.year
                mes = fecha.month
                dia = fecha.day
                return ((abs(año-1900) + (mes - 1) / 12) + ((dia - 1) / 365.25))

            df_calculos['FJ'] = df_calculos['fecha'].apply(fecha_juliana)
            df_calculos['R'] = ((C12 - df_calculos['FJ']) / C13) * 5
            df_calculos['H'] = C14 * (nivel_embalse_max - df_calculos['nivel_embalse']) / (
                        nivel_embalse_max - nivel_embalse_min)
            df_calculos['beta'] = (df_calculos['FJ'] - df_calculos['A']) * 2 * np.pi / 360

            df_calculos['H'] = df_calculos['H'].astype(float)

            # Funciones
            df_calculos['f0'] = 1
            df_calculos['f1'] = np.exp(df_calculos['R'])
            df_calculos['f2'] = np.exp(-df_calculos['R'])
            df_calculos['f3'] = df_calculos['H'] ** 0.5
            df_calculos['f4'] = df_calculos['H']
            df_calculos['f5'] = df_calculos['H'] ** 2
            df_calculos['f6'] = df_calculos['H'] ** 3
            df_calculos['f7'] = np.cos(df_calculos['beta'])
            df_calculos['f8'] = np.sin(df_calculos['beta'])
            df_calculos['f9'] = np.sin(df_calculos['beta']) ** 2
            df_calculos['f10'] = np.sin(df_calculos['beta']) * np.cos(df_calculos['beta'])

            cols_f = ['f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10']
            for col in cols_f:
                df_calculos[col] = pd.to_numeric(df_calculos[col], errors='coerce').astype(float)
            df_calculos['valor'] = pd.to_numeric(df_calculos['valor'], errors='coerce').astype(
                float)

            X = df_calculos[cols_f].values
            y = df_calculos['valor'].values

            C, _, _, _ = np.linalg.lstsq(X, y, rcond=None)

            df_calculos['yc'] = (
                    C[0] * df_calculos['f0'] + C[1] * df_calculos['f1'] + C[2] * df_calculos['f2'] +
                    C[3] * df_calculos['f3'] + C[4] * df_calculos['f4'] + C[5] * df_calculos['f5'] +
                    C[6] * df_calculos['f6'] + C[7] * df_calculos['f7'] + C[8] * df_calculos['f8'] +
                    C[9] * df_calculos['f9'] + C[10] * df_calculos['f10']
            )

            df_calculos['error'] = df_calculos['valor'] - df_calculos['yc']

            # Crear DataFrame para extrapolación
            df_extrapolacion = pd.DataFrame({
                'fecha': fechas_supuestas,
                'nivel_embalse': niveles_embalse_supuestos
            })
            df_extrapolacion['fecha'] = pd.to_datetime(df_extrapolacion['fecha'])
            df_extrapolacion['nivel_embalse'] = pd.to_numeric(df_extrapolacion['nivel_embalse'],
                                                              errors='coerce').astype(float)

            # Valor medio de las mediciones históricas
            Xmedio = df_calculos['valor'].mean()

            # Número de muestras disponibles
            n = len(df_calculos)

            # EMCo (Error Medio Cuadrático Inicial)
            EMCo = np.sqrt(((df_calculos['valor'] - Xmedio) ** 2).sum() / (n - 1))

            # Número de términos involucrados en el ajuste
            Nterm = len(cols_f)  # Número de funciones utilizadas en la regresión

            # EMC (Error Medio Cuadrático Residual)
            EMC = np.sqrt(((df_calculos['valor'] - df_calculos['yc']) ** 2).sum() / (n - 1 - Nterm))

            # Calcular índice de correlación entre nivel de embalse y nivel piezométrico
            correlacion = df_calculos[['nivel_embalse', 'valor']].corr().iloc[0, 1] * 100  # En porcentaje

            # Calcular desviación estándar de los valores medidos
            std_valor = df_calculos['valor'].std()


            context['EMCo'] = EMCo
            context['EMC'] = EMC
            context['correlacion'] = correlacion
            context['std_valor'] = std_valor

            # --- Cálculos para Extrapolación ---
            df_calculos_extrapolacion = df_extrapolacion.copy()

            df_calculos_extrapolacion['A'] = df_calculos_extrapolacion['fecha'].dt.year - 1900

            df_calculos_extrapolacion['FJ'] = df_calculos_extrapolacion['fecha'].apply(fecha_juliana)
            df_calculos_extrapolacion['R'] = ((C12 - df_calculos_extrapolacion['FJ']) / C13) * 5
            df_calculos_extrapolacion['H'] = C14 * (nivel_embalse_max - df_calculos_extrapolacion['nivel_embalse']) / (
                        nivel_embalse_max - nivel_embalse_min)
            df_calculos_extrapolacion['beta'] = (df_calculos_extrapolacion['FJ'] - df_calculos_extrapolacion[
                'A']) * 2 * np.pi / 360

            df_calculos_extrapolacion['H'] = df_calculos_extrapolacion['H'].astype(float)

            # Funciones
            df_calculos_extrapolacion['f0'] = 1
            df_calculos_extrapolacion['f1'] = np.exp(df_calculos_extrapolacion['R'])
            df_calculos_extrapolacion['f2'] = np.exp(-df_calculos_extrapolacion['R'])
            df_calculos_extrapolacion['f3'] = df_calculos_extrapolacion['H'] ** 0.5
            df_calculos_extrapolacion['f4'] = df_calculos_extrapolacion['H']
            df_calculos_extrapolacion['f5'] = df_calculos_extrapolacion['H'] ** 2
            df_calculos_extrapolacion['f6'] = df_calculos_extrapolacion['H'] ** 3
            df_calculos_extrapolacion['f7'] = np.cos(df_calculos_extrapolacion['beta'])
            df_calculos_extrapolacion['f8'] = np.sin(df_calculos_extrapolacion['beta'])
            df_calculos_extrapolacion['f9'] = np.sin(df_calculos_extrapolacion['beta']) ** 2
            df_calculos_extrapolacion['f10'] = np.sin(df_calculos_extrapolacion['beta']) * np.cos(
                df_calculos_extrapolacion['beta'])

            X_extrapolacion = df_calculos_extrapolacion[cols_f].values
            df_calculos_extrapolacion['yc'] = np.dot(X_extrapolacion, C)

            if fechas_supuestas and niveles_embalse_supuestos:
                df_resultado = pd.concat([df_calculos, df_calculos_extrapolacion], ignore_index=True, sort=False)
            else:
                df_resultado = df_calculos.copy()

            df_resultado = df_resultado.replace({np.nan: None})

            # Calcular los límites superior e inferior de la banda de normalidad
            df_resultado['banda_superior'] = df_resultado['yc'] + 2 * std_valor
            df_resultado['banda_inferior'] = df_resultado['yc'] - 2 * std_valor

            # Crear diccionario para el template
            datos_para_template = df_resultado.to_dict(orient='records')

            #
            fig = go.Figure()

            # Nivel de embalse
            fig.add_trace(go.Scatter(
                x=df_resultado['fecha'],
                y=df_resultado['nivel_embalse'],
                mode='lines',
                name='NE'
            ))

            # Datos reales
            fig.add_trace(go.Scatter(
                x=df_resultado['fecha'],
                y=df_resultado['valor'],
                mode='markers',
                name=tipo_medicion + ' (Medido)'
            ))

            # Datos calculados (ajuste)
            fig.add_trace(go.Scatter(
                x=df_resultado['fecha'],
                y=df_resultado['yc'],
                mode='lines',
                name=tipo_medicion + ' (Calculado)'
            ))

            # Banda de normalidad
            fig.add_trace(go.Scatter(
                x=df_resultado['fecha'],
                y=df_resultado['banda_superior'],
                mode='lines',
                name='Umbral de Normalidad',
                line=dict(color='#FFA500')
            ))

            fig.add_trace(go.Scatter(
                x=df_resultado['fecha'],
                y=df_resultado['banda_inferior'],
                mode='lines',
                name='Umbral de Normalidad',
                line=dict(color='#FFA500')
            ))

            # Datos extrapolados
            if fechas_supuestas and niveles_embalse_supuestos:
                fig.add_trace(go.Scatter(
                    x=df_calculos_extrapolacion['fecha'],
                    y=df_calculos_extrapolacion['yc'],
                    mode='lines+markers',
                    name=tipo_medicion + ' (Extrapolado)'
                ))

            fig.update_layout(
                title='Fecha Nivel vs. ' + tipo_medicion + ' ' + nombre_instrumento,
                xaxis_title='Fecha',
                yaxis_title=tipo_medicion,
                height=600,
                showlegend=True,
                template='plotly_white',
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=2, label="Último año", step="year", stepmode="backward"),
                            dict(count=3, label="Últimos 3 años", step="year", stepmode="backward"),
                            dict(step="all", label="Todos")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                )
            )

            # Convertir el gráfico a HTML para el template
            plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

            context['datos_calculados'] = datos_para_template
            context['constantes_C'] = C.tolist()
            context['plot_div'] = plot_div

            return render(request, 'predicciones_modelos.html', context)

        except Exception as e:
            print(f"Error: {e}")
            context['error'] = f'Ocurrió un error al procesar la solicitud: {e}'
            return render(request, 'predicciones_modelos.html', context)

    else:
        instrumentos_activos = Instrumento.objects.filter(activo=True)
        context['instrumentos_activos'] = instrumentos_activos
        return render(request, 'predicciones_modelos.html', context)



