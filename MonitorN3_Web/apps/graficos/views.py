import json
from django.http import JsonResponse
from django.shortcuts import render
import plotly.graph_objects as go
import pandas as pd
from .forms.personalizados_form import PersonalizadoForm
from ..instrumento.models import Instrumento
from ..embalse.models import Embalse
from ..medicion.models import Medicion

GRAFICOS_PREDEFINIDOS = {
    "fecha_nivel_embalse": "Fecha - Nivel Embalse",
    "fecha_nivel_piezometrico_pc1_7": "Fecha - Nivel Piezométrico (PC1-2-3-4-5-6-7)",
    "fecha_nivel_piezometrico_pc1_5_6": "Fecha - Nivel Piezométrico (PC1-5-6)",
    "fecha_nivel_piezometrico_f1_pc2_3_4": "Fecha - Nivel Piezométrico (F1-PC2-3-4)",
    "nivel_embalse_nivel_piezometrico_pc1_5_6": "Nivel Embalse - Nivel Piezométrico (PC1-5-6)",
    "nivel_embalse_nivel_piezometrico_f1_pc2_3_4": "Nivel Embalse - Nivel Piezométrico (F1-PC2-3-4)",
    "nivel_embalse_nivel_freatico_f1": "Nivel Embalse - Nivel Freático (F1)",
    "nivel_embalse_caudal_afo3_tot": "Nivel Embalse - Caudal (AFo3-TOT)",
    "nivel_embalse_caudal_afo3_ei": "Nivel Embalse - Caudal (AFo3-EI)",
    "nivel_embalse_caudal_afo3_pp": "Nivel Embalse - Caudal (AFo3-PP)",
    "fecha_nivel_embalse_caudal_afo3_tot": "Fecha - Nivel Embalse - Caudal (AFo3-TOT)",
    "fecha_nivel_embalse_caudal_afo3_pp": "Fecha - Nivel Embalse - Caudal (AFo3-PP)",
}

def predefinidos(request):
    return render(request, "predefinidos.html", {"graficos": GRAFICOS_PREDEFINIDOS})

def generar_grafico_predefinido(request):
    graficos = GRAFICOS_PREDEFINIDOS
    grafico_html = None

    if request.method == "POST":
        seleccion = request.POST.get("grafico_seleccionado")

        if seleccion == "fecha_nivel_embalse":
            datos = Embalse.objects.all().values("fecha", "nivel_embalse")
            df = pd.DataFrame(list(datos))
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df["fecha"],
                    y=df["nivel_embalse"],
                    mode="lines+markers",
                    name="Nivel Embalse",
                    connectgaps=True
                )
            )
            fig.update_layout(
                title="Fecha - Nivel Embalse",
                xaxis_title="Fecha",
                yaxis_title="Nivel Embalse (msnm)"
            )

        elif seleccion == "fecha_nivel_piezometrico_pc1_7":
            piezometros = ["L3-PC1", "L3-PC2", "L3-PC3", "L3-PC4", "L3-PC5", "L3-PC6", "L3-PC7"]
            datos = Medicion.objects.filter(id_instrumento__nombre__in=piezometros).values("fecha", "valor", "id_instrumento__nombre")
            df = pd.DataFrame(list(datos))

            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            fig = go.Figure()
            for piezometro in piezometros:
                datos_piezometro = df[df["id_instrumento__nombre"] == piezometro]
                fig.add_trace(
                    go.Scatter(
                        x=datos_piezometro["fecha"],
                        y=datos_piezometro["valor"],
                        mode="lines+markers",
                        name=piezometro
                    )
                )

            fig.update_layout(
                title="Fecha - Nivel Piezométrico (PC1-2-3-4-5-6-7)",
                xaxis_title="Fecha",
                yaxis_title="Nivel Piezométrico (msnm)"
            )

        elif seleccion == "fecha_nivel_piezometrico_pc1_5_6":
            piezometros = ["L3-PC1", "L3-PC5", "L3-PC6"]
            datos = Medicion.objects.filter(id_instrumento__nombre__in=piezometros).values("fecha", "valor", "id_instrumento__nombre")

            df = pd.DataFrame(list(datos))

            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            fig = go.Figure()
            for piezometro in piezometros:
                datos_piezometro = df[df["id_instrumento__nombre"] == piezometro]
                fig.add_trace(
                    go.Scatter(
                        x=datos_piezometro["fecha"],
                        y=datos_piezometro["valor"],
                        mode="lines+markers",
                        name=piezometro
                    )
                )
            fig.update_layout(
                title="Fecha - Nivel Piezométrico (PC1_5_6)",
                xaxis_title="Fecha",
                yaxis_title="Nivel Piezométrico (msnm)"
            )

        elif seleccion == "fecha_nivel_piezometrico_f1_pc2_3_4":
            instrumentos = ["L3-F1", "L3-PC2", "L3-PC3", "L3-PC4"]
            datos = Medicion.objects.filter(id_instrumento__nombre__in=instrumentos).values("fecha", "valor", "id_instrumento__nombre")

            df = pd.DataFrame(list(datos))

            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            fig = go.Figure()
            for instrumento in instrumentos:
                datos_instrumentos = df[df["id_instrumento__nombre"] == instrumento]
                fig.add_trace(
                    go.Scatter(
                        x=datos_instrumentos["fecha"],
                        y=datos_instrumentos["valor"],
                        mode="lines+markers",
                        name=instrumento
                    )
                )
            fig.update_layout(
                title="Fecha - Nivel Piezométrico (F1_PC2_3_4)",
                xaxis_title="Fecha",
                yaxis_title="Nivel Piezométrico (msnm)"
            )

        elif seleccion == "nivel_embalse_nivel_piezometrico_pc1_5_6":
            piezometros = ["L3-PC1", "L3-PC5", "L3-PC6"]
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            piezometro_data = Medicion.objects.filter(id_instrumento__nombre__in=piezometros).values("fecha", "valor", "id_instrumento__nombre")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_piezometro = pd.DataFrame(list(piezometro_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_piezometro["fecha"] = pd.to_datetime(df_piezometro["fecha"])

            df_final = pd.merge(df_piezometro, df_embalse, on="fecha", how="inner")

            df_final["año"] = df_final["fecha"].dt.year
            print(df_final)
            fig = go.Figure()

            for piezometro in piezometros:
                df_pz = df_final[df_final["id_instrumento__nombre"] == piezometro]

                for año in df_pz["año"].unique():
                    df_año = df_pz[df_pz["año"] == año]
                    fig.add_trace(
                        go.Scatter(
                            x=df_año["nivel_embalse"],
                            y=df_año["valor"],
                            mode="markers",
                            name=f"{piezometro} ({año})",
                            marker=dict(symbol="circle", size=8)
                        )
                    )
            fig.update_layout(
                title="Nivel Embalse - Nivel Piezométrico (PC1-5-6)",
                xaxis_title="Nivel Embalse (msnm)",
                yaxis_title="Nivel Piezométrico (msnm)",
                legend_title="Piezómetro (Año)"
            )

        elif seleccion == "nivel_embalse_nivel_piezometrico_f1_pc2_3_4":
            piezometros = ["L3-F1", "L3-PC2", "L3-PC3", "L3-PC4"]
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            piezometro_data = Medicion.objects.filter(id_instrumento__nombre__in=piezometros).values("fecha", "valor", "id_instrumento__nombre")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_piezometro = pd.DataFrame(list(piezometro_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_piezometro["fecha"] = pd.to_datetime(df_piezometro["fecha"])

            df_final = pd.merge(df_piezometro, df_embalse, on="fecha", how="inner")

            df_final["año"] = df_final["fecha"].dt.year
            print(df_final)
            fig = go.Figure()

            for piezometro in piezometros:
                df_pz = df_final[df_final["id_instrumento__nombre"] == piezometro]

                for año in df_pz["año"].unique():
                    df_año = df_pz[df_pz["año"] == año]
                    fig.add_trace(
                        go.Scatter(
                            x=df_año["nivel_embalse"],
                            y=df_año["valor"],
                            mode="markers",
                            name=f"{piezometro} ({año})",
                            marker=dict(symbol="circle", size=8)
                        )
                    )
            fig.update_layout(
                title="Nivel Embalse - Nivel Piezométrico (F1-PC2-3-4)",
                xaxis_title="Nivel Embalse (msnm)",
                yaxis_title="Nivel Piezométrico (msnm)",
                legend_title="Piezómetro (Año)"
            )

        elif seleccion == "nivel_embalse_nivel_freatico_f1":
            freatimetros = ["L3-F1"]
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            freatimetro_data = Medicion.objects.filter(id_instrumento__nombre__in=freatimetros).values("fecha", "valor", "id_instrumento__nombre")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_freatimetro = pd.DataFrame(list(freatimetro_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_freatimetro["fecha"] = pd.to_datetime(df_freatimetro["fecha"])

            df_final = pd.merge(df_freatimetro, df_embalse, on="fecha", how="inner")

            df_final["año"] = df_final["fecha"].dt.year
            print(df_final)
            fig = go.Figure()

            for freatimetro in freatimetros:
                df_pz = df_final[df_final["id_instrumento__nombre"] == freatimetro]

                for año in df_pz["año"].unique():
                    df_año = df_pz[df_pz["año"] == año]
                    fig.add_trace(
                        go.Scatter(
                            x=df_año["nivel_embalse"],
                            y=df_año["valor"],
                            mode="markers",
                            name=f"{freatimetro} ({año})",
                            marker=dict(symbol="circle", size=8)
                        )
                    )
            fig.update_layout(
                title="Nivel Embalse - Nivel Freático (L3-F1)",
                xaxis_title="Nivel Embalse (msnm)",
                yaxis_title="Nivel Freático (msnm)",
                legend_title="Freatímetro (Año)"
            )

        elif seleccion == "nivel_embalse_caudal_afo3_tot":
            aforadores = ["AFo3-TOT"]
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            aforador_data = Medicion.objects.filter(id_instrumento__nombre__in=aforadores).values("fecha", "valor", "id_instrumento__nombre")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_aforador = pd.DataFrame(list(aforador_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_aforador["fecha"] = pd.to_datetime(df_aforador["fecha"])

            df_final = pd.merge(df_aforador, df_embalse, on="fecha", how="inner")

            df_final["año"] = df_final["fecha"].dt.year
            print(df_final)
            fig = go.Figure()

            for aforador in aforadores:
                df_pz = df_final[df_final["id_instrumento__nombre"] == aforador]

                for año in df_pz["año"].unique():
                    df_año = df_pz[df_pz["año"] == año]
                    fig.add_trace(
                        go.Scatter(
                            x=df_año["nivel_embalse"],
                            y=df_año["valor"],
                            mode="markers",
                            name=f"{aforador} ({año})",
                            marker=dict(symbol="circle", size=8)
                        )
                    )
            fig.update_layout(
                title="Nivel Embalse - Caudal (AFo3-TOT)",
                xaxis_title="Nivel Embalse (msnm)",
                yaxis_title="Caudal (m³/s)",
                legend_title="Aforador (Año)"
            )

        elif seleccion == "nivel_embalse_caudal_afo3_ei":
            aforadores = ["AFo3-EI"]
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            aforador_data = Medicion.objects.filter(id_instrumento__nombre__in=aforadores).values("fecha", "valor", "id_instrumento__nombre")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_aforador = pd.DataFrame(list(aforador_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_aforador["fecha"] = pd.to_datetime(df_aforador["fecha"])

            df_final = pd.merge(df_aforador, df_embalse, on="fecha", how="inner")

            df_final["año"] = df_final["fecha"].dt.year
            print(df_final)
            fig = go.Figure()

            for aforador in aforadores:
                df_pz = df_final[df_final["id_instrumento__nombre"] == aforador]

                for año in df_pz["año"].unique():
                    df_año = df_pz[df_pz["año"] == año]
                    fig.add_trace(
                        go.Scatter(
                            x=df_año["nivel_embalse"],
                            y=df_año["valor"],
                            mode="markers",
                            name=f"{aforador} ({año})",
                            marker=dict(symbol="circle", size=8)
                        )
                    )
            fig.update_layout(
                title="Nivel Embalse - Caudal (AFo3-TOT)",
                xaxis_title="Nivel Embalse (msnm)",
                yaxis_title="Caudal (l/s)",
                legend_title="Aforador (Año)"
            )

        elif seleccion == "nivel_embalse_caudal_afo3_pp":
            aforadores = ["AFo3-PP"]
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            aforador_data = Medicion.objects.filter(id_instrumento__nombre__in=aforadores).values("fecha", "valor", "id_instrumento__nombre")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_aforador = pd.DataFrame(list(aforador_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_aforador["fecha"] = pd.to_datetime(df_aforador["fecha"])

            df_final = pd.merge(df_aforador, df_embalse, on="fecha", how="inner")

            df_final["año"] = df_final["fecha"].dt.year
            print(df_final)
            fig = go.Figure()

            for aforador in aforadores:
                df_pz = df_final[df_final["id_instrumento__nombre"] == aforador]

                for año in df_pz["año"].unique():
                    df_año = df_pz[df_pz["año"] == año]
                    fig.add_trace(
                        go.Scatter(
                            x=df_año["nivel_embalse"],
                            y=df_año["valor"],
                            mode="markers",
                            name=f"{aforador} ({año})",
                            marker=dict(symbol="circle", size=8)
                        )
                    )
            fig.update_layout(
                title="Nivel Embalse - Caudal (AFo3-TOT)",
                xaxis_title="Nivel Embalse (msnm)",
                yaxis_title="Caudal (l/s)",
                legend_title="Aforador (Año)"
            )

        elif seleccion == "fecha_nivel_embalse_caudal_afo3_tot":
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            caudal_data = Medicion.objects.filter(id_instrumento__nombre="AFo3-TOT").values("fecha", "valor")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_caudal = pd.DataFrame(list(caudal_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_caudal["fecha"] = pd.to_datetime(df_caudal["fecha"])

            df_final = pd.merge(df_embalse, df_caudal, on="fecha", how="outer", suffixes=("_embalse", "_caudal"))
            df_final = df_final.sort_values("fecha")

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df_final["fecha"],
                    y=df_final["nivel_embalse"],
                    mode="lines+markers",
                    name="Nivel Embalse",
                    yaxis="y1",
                    connectgaps=True
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df_final["fecha"],
                    y=df_final["valor"],
                    mode="lines+markers",
                    name="Caudal (AFo3-TOT)",
                    yaxis="y2",
                    connectgaps=True
                )
            )

            fig.update_layout(
                title="Fecha - Nivel Embalse - Caudal (AFo3-TOT)",
                xaxis_title="Fecha",
                yaxis=dict(title="Nivel Embalse (msnm)", side="left", showgrid=True),
                yaxis2=dict(title="Caudal (m³/s)", overlaying="y", side="right", showgrid=True),
            )

        elif seleccion == "fecha_nivel_embalse_caudal_afo3_pp":
            embalse_data = Embalse.objects.all().values("fecha", "nivel_embalse")
            caudal_data = Medicion.objects.filter(id_instrumento__nombre="AFo3-PP").values("fecha", "valor")

            df_embalse = pd.DataFrame(list(embalse_data))
            df_caudal = pd.DataFrame(list(caudal_data))

            df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])
            df_caudal["fecha"] = pd.to_datetime(df_caudal["fecha"])

            df_final = pd.merge(df_embalse, df_caudal, on="fecha", how="outer", suffixes=("_embalse", "_caudal"))
            df_final = df_final.sort_values("fecha")

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df_final["fecha"],
                    y=df_final["nivel_embalse"],
                    mode="lines+markers",
                    name="Nivel Embalse",
                    yaxis="y1",
                    connectgaps=True
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df_final["fecha"],
                    y=df_final["valor"],
                    mode="lines+markers",
                    name="Caudal (AFo3-PP)",
                    yaxis="y2",
                    connectgaps=True
                )
            )

            fig.update_layout(
                title="Fecha - Nivel Embalse - Caudal (AFo3-PP)",
                xaxis_title="Fecha",
                yaxis=dict(title="Nivel Embalse (msnm)", side="left", showgrid=True),
                yaxis2=dict(title="Caudal (l/s)", overlaying="y", side="right", showgrid=True),
            )

        if "fig" in locals():
            grafico_html = fig.to_html(full_html=False)
        return render(request, "predefinidos.html",  {"graficos": graficos, "grafico": grafico_html})

    return render(request, "predefinidos.html")

def personalizados(request):
    form = PersonalizadoForm()

    piezometros = list(Instrumento.objects.filter(id_tipo__nombre_tipo="PIEZÓMETRO").values("id", "nombre"))
    freatimetros = list(Instrumento.objects.filter(id_tipo__nombre_tipo="FREATÍMETRO").values("id", "nombre"))
    aforadores = list(Instrumento.objects.filter(id_tipo__nombre_tipo__icontains="AFORADOR").values("id", "nombre"))

    contexto = {
        "personalizados_form": form,
        "piezometros_json": json.dumps(piezometros),
        "freatimetros_json": json.dumps(freatimetros),
        "aforadores_json": json.dumps(aforadores)
    }

    return render(request, "personalizados_form.html", contexto)

def generar_grafico(request):
    if request.method not in ["POST", "GET"]:
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data = request.POST.copy()

    for campo in ["instrumento_x", "instrumento_y", "instrumento_y2"]:
        if campo in data:
            data.setlist(campo, [int(i) for i in data.getlist(campo) if i.isdigit()])

    form = PersonalizadoForm(data)

    if not form.is_valid():
        print("❌ Error en el formulario:", form.errors)
        return JsonResponse({"error": form.errors}, status=400)

    tipo_grafico = form.cleaned_data["tipo_grafico"]
    tipo_grafico_y2 = form.cleaned_data.get("tipo_grafico_y2")
    eje_x = form.cleaned_data["eje_x"]
    eje_y = form.cleaned_data["eje_y"]
    instrumentos_x = form.cleaned_data["instrumento_x"]
    instrumentos_y = form.cleaned_data["instrumento_y"]
    agregar_eje_y_secundario = form.cleaned_data["agregar_eje_y_secundario"]
    eje_y_secundario = form.cleaned_data["eje_y_secundario"]
    instrumentos_y2 = form.cleaned_data["instrumento_y2"]

    try:
        fechas_embalse = Embalse.objects.values("fecha").distinct()
        fechas_medicion = Medicion.objects.values("fecha").distinct()
        todas_las_fechas = pd.DataFrame(list(fechas_embalse) + list(fechas_medicion)).drop_duplicates().sort_values("fecha")
        todas_las_fechas["fecha"] = pd.to_datetime(todas_las_fechas["fecha"])

        #Datos eje X
        df_x = todas_las_fechas.copy()
        if eje_x == "nivel_embalse":
            df_x = pd.DataFrame(list(Embalse.objects.values("fecha", "nivel_embalse")))
            df_x.rename(columns={"nivel_embalse": "valor_x"}, inplace=True)
        elif eje_x in ["nivel_piezometrico", "nivel_freatico", "caudal"] and instrumentos_x:
            datos_x = Medicion.objects.filter(id_instrumento__in=instrumentos_x).values("fecha", "valor", "id_instrumento__nombre")
            df_x = pd.DataFrame(list(datos_x))
            df_grouped = df_x.groupby(["fecha", "id_instrumento__nombre"])["valor"].mean().reset_index()
            df_x = df_grouped.pivot(index="fecha", columns="id_instrumento__nombre", values="valor").reset_index()

        df_x["fecha"] = pd.to_datetime(df_x["fecha"])

        #Datos eje Y
        df_y = todas_las_fechas.copy()
        if eje_y == "nivel_embalse":
            df_y = pd.DataFrame(list(Embalse.objects.values("fecha", "nivel_embalse")))
            df_y.rename(columns={"nivel_embalse": "valor_y"}, inplace=True)
        elif eje_y in ["nivel_piezometrico", "nivel_freatico", "caudal"] and instrumentos_y:
            datos_y = Medicion.objects.filter(id_instrumento__in=instrumentos_y).values("fecha", "valor", "id_instrumento__nombre")
            df_y = pd.DataFrame(list(datos_y))
            df_grouped = df_y.groupby(["fecha", "id_instrumento__nombre"])["valor"].mean().reset_index()
            df_y = df_grouped.pivot(index="fecha", columns="id_instrumento__nombre", values="valor").reset_index()

        df_y["fecha"] = pd.to_datetime(df_y["fecha"])

        #Datos eje Y Secundario (si está habilitado)
        df_y2 = None
        if agregar_eje_y_secundario and eje_y_secundario and instrumentos_y2:
            datos_y2 = Medicion.objects.filter(id_instrumento__in=instrumentos_y2).values("fecha", "valor", "id_instrumento__nombre")
            df_y2 = pd.DataFrame(list(datos_y2))
            df_grouped = df_y2.groupby(["fecha", "id_instrumento__nombre"])["valor"].mean().reset_index()
            df_y2 = df_grouped.pivot(index="fecha", columns="id_instrumento__nombre", values="valor").reset_index()

            df_y2["fecha"] = pd.to_datetime(df_y2["fecha"])

        #Unión de DataFrames
        df_final = df_x.merge(df_y, on="fecha", how="outer")
        if df_y2 is not None:
            df_final = df_final.merge(df_y2, on="fecha", how="outer")

        df_final.sort_values("fecha", inplace=True)
        #print(df_final)

        #Generar el gráfico
        fig = go.Figure()

        nombres_ejes = {
            "fecha": "Fecha",
            "nivel_embalse": "Nivel Embalse [msnm]",
            "nivel_piezometrico": "Nivel Piezométrico [msnm]",
            "nivel_freatico": "Nivel Freático [msnm]",
            "caudal": "Caudal [l/s - m³/s]"
        }

        eje_x_valores = df_final["fecha"] if eje_x == "fecha" else df_final["valor_x"]

        if "valor_y" in df_final.columns and eje_y == "nivel_embalse":
            fig.add_trace(
                get_trace(
                    tipo_grafico,
                    df_final["fecha"],
                    df_final["valor_y"],
                    "Nivel Embalse"
                )
            )

        #Agregar trazas para cada instrumento del eje Y
        for instrumento in instrumentos_y:
            if instrumento.nombre in df_final.columns:
                fig.add_trace(
                    get_trace(
                        tipo_grafico,
                        eje_x_valores,
                        df_final[instrumento.nombre],
                        instrumento.nombre
                    )
                )

        # Agregar trazas para cada instrumento del eje Y secundario
        if df_y2 is not None:
            for instrumento in instrumentos_y2:
                if instrumento.nombre in df_final.columns:
                    fig.add_trace(
                        get_trace(
                            tipo_grafico_y2,
                            eje_x_valores,
                            df_final[instrumento.nombre],
                            instrumento.nombre,
                                  "y2"
                        )
                    )

            fig.update_layout(
                yaxis2=dict(
                    title=nombres_ejes[eje_y_secundario],
                    overlaying="y",
                    side="right"
                )
            )

        fig.update_layout(
            title="Gráfico",
            xaxis_title=nombres_ejes[eje_x],
            yaxis_title=nombres_ejes[eje_y]
        )

        return JsonResponse({"grafico": fig.to_html(full_html=False)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_trace(tipo_grafico, x_values, y_values, eje_nombre, yaxis=None):
    if tipo_grafico == "bar":
        return go.Bar(x=x_values, y=y_values, name=eje_nombre, yaxis=yaxis)
    elif tipo_grafico == "scatter":
        return go.Scatter(x=x_values, y=y_values, mode="markers", name=eje_nombre, yaxis=yaxis)
    else:
        return go.Scatter(x=x_values, y=y_values, mode="lines+markers",connectgaps=True, name=eje_nombre, yaxis=yaxis)