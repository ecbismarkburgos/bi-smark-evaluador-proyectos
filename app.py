import streamlit as st
import pandas as pd
import numpy_financial as npf
from io import BytesIO
from modules.amortizacion import generar_amortizacion
from modules.evaluacion import evaluar_proyecto

st.set_page_config(
    page_title="Evaluador de Proyectos BI-SMARK",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Evaluador de Proyectos de Inversión")
st.write("Primera versión del generador de cálculos financieros de BI-SMARK.")

st.subheader("Datos del proyecto")

monto_proyecto = st.number_input(
    "Monto total del proyecto",
    min_value=0.0,
    value=100000.0,
    step=1000.0
)

monto_financiado = st.number_input(
    "Monto financiado",
    min_value=0.0,
    value=70000.0,
    step=1000.0
)

tasa_interes = st.number_input(
    "Tasa efectiva anual del financiamiento (%)",
    min_value=0.0,
    value=10.0,
    step=0.1
)

plazo_credito = st.number_input(
    "Plazo del financiamiento",
    min_value=1,
    value=5,
    step=1
)

unidad_plazo_credito = st.selectbox(
    "Unidad del plazo del financiamiento",
    ["Años", "Meses"]
)

frecuencia_pago = st.selectbox(
    "Frecuencia de pagos",
    ["Mensual", "Trimestral", "Semestral", "Anual"]
)

tipo_amortizacion = st.selectbox(
    "Tipo de amortización",
    ["Francés", "Alemán"]
)

tipo_gracia = st.selectbox(
    "Tipo de período de gracia",
    [
        "Sin gracia",
        "Gracia de capital",
        "Gracia total"
    ]
)

meses_gracia = st.number_input(
    "Período de gracia (meses)",
    min_value=0,
    value=0,
    step=1,
    disabled=(tipo_gracia == "Sin gracia"),
    help=(
        "En gracia de capital se pagan únicamente intereses. "
        "En gracia total no se realizan pagos y los intereses "
        "se incorporan al saldo de la deuda."
    )
)

st.subheader("Operación")

mes_inicio_operaciones = st.number_input(
    "Mes de inicio de operaciones",
    min_value=1,
    value=1,
    step=1,
    help="Mes en el que el proyecto comienza a generar ingresos y costos operativos."
)

costos_fijos = st.number_input(
    "Costos fijos mensuales",
    min_value=0.0,
    value=2000.0,
    step=100.0
)

costos_variables = st.number_input(
    "Costos variables mensuales",
    min_value=0.0,
    value=3500.0,
    step=100.0
)

ingresos = st.number_input(
    "Ingresos mensuales estimados",
    min_value=0.0,
    value=9000.0,
    step=100.0
)

st.subheader("Evaluación")

horizonte_proyecto = st.number_input(
    "Horizonte de evaluación del proyecto",
    min_value=1,
    value=10,
    step=1
)

unidad_horizonte = st.selectbox(
    "Unidad del horizonte de evaluación",
    ["Años", "Meses"]
)

tasa_descuento = st.number_input(
    "Tasa de descuento anual (%)",
    min_value=0.0,
    value=12.0,
    step=0.1
)

if st.button("Calcular proyecto"):

    # --------------------------------------------------
    # VALIDACIONES BÁSICAS
    # --------------------------------------------------

    if monto_financiado > monto_proyecto:
        st.error(
            "El monto financiado no puede ser mayor que el monto total del proyecto."
        )
        st.stop()

    # --------------------------------------------------
    # CÁLCULOS INICIALES
    # --------------------------------------------------

    aporte_propio = monto_proyecto - monto_financiado

    flujo_operativo = (
        ingresos
        - costos_fijos
        - costos_variables
    )

    # --------------------------------------------------
    # CONVERSIÓN DE PLAZOS A MESES
    # --------------------------------------------------

    # Plazo del financiamiento

    if unidad_plazo_credito == "Años":
        plazo_credito_meses = plazo_credito * 12
    else:
        plazo_credito_meses = plazo_credito

    # Horizonte de evaluación del proyecto

    if unidad_horizonte == "Años":
        horizonte_meses = horizonte_proyecto * 12
    else:
        horizonte_meses = horizonte_proyecto

    # Validar que el inicio de operaciones
    # esté dentro del horizonte del proyecto

    if mes_inicio_operaciones > horizonte_meses:
        st.error(
            "El mes de inicio de operaciones no puede ser mayor "
            "que el horizonte de evaluación del proyecto."
        )
        st.stop()

    # Por ahora exigiremos que todo el crédito termine
    # dentro del horizonte evaluado.

    if plazo_credito_meses > horizonte_meses:
        st.error(
            "El plazo del financiamiento no puede superar "
            "el horizonte de evaluación del proyecto."
        )
        st.stop()

    # --------------------------------------------------
    # FRECUENCIA DE PAGOS
    # --------------------------------------------------

    meses_por_pago = {
        "Mensual": 1,
        "Trimestral": 3,
        "Semestral": 6,
        "Anual": 12
    }

    frecuencia_meses = meses_por_pago[frecuencia_pago]

    numero_pagos = plazo_credito_meses / frecuencia_meses

    # Validar que el plazo sea compatible con la frecuencia
    if numero_pagos != int(numero_pagos):
        st.error(
            "El plazo seleccionado no es compatible con la frecuencia de pagos."
        )
        st.stop()

    numero_pagos = int(numero_pagos)

    # --------------------------------------------------
    # PERÍODO DE GRACIA
    # --------------------------------------------------

    if tipo_gracia == "Sin gracia":
        meses_gracia_calculo = 0
    else:
        meses_gracia_calculo = meses_gracia

    # La gracia debe coincidir con la frecuencia de pago

    if meses_gracia_calculo % frecuencia_meses != 0:
        st.error(
            "El período de gracia debe ser compatible con "
            "la frecuencia de pagos."
        )
        st.stop()

    periodos_gracia = int(
        meses_gracia_calculo / frecuencia_meses
    )

    # Debe quedar al menos un período para amortizar capital

    if (
        monto_financiado > 0
        and periodos_gracia >= numero_pagos
    ):
        st.error(
            "El período de gracia debe ser menor que "
            "el plazo total del financiamiento."
        )
        st.stop()

    periodos_amortizacion = (
        numero_pagos - periodos_gracia
    )

    # --------------------------------------------------
    # CONVERSIÓN DE LA TASA EFECTIVA ANUAL
    # --------------------------------------------------

    tasa_anual_decimal = tasa_interes / 100

    periodos_por_ano = 12 / frecuencia_meses

    tasa_periodica = (
        (1 + tasa_anual_decimal) ** (1 / periodos_por_ano)
        - 1
    )


    # --------------------------------------------------
    # TABLA DE AMORTIZACIÓN
    # --------------------------------------------------

    df_amortizacion = generar_amortizacion(
        monto_financiado=monto_financiado,
        tasa_periodica=tasa_periodica,
        numero_pagos=numero_pagos,
        periodos_gracia=periodos_gracia,
        tipo_gracia=tipo_gracia,
        tipo_amortizacion=tipo_amortizacion
    )

    # --------------------------------------------------
    # RESUMEN DEL PERÍODO DE GRACIA
    # --------------------------------------------------

    intereses_capitalizados = 0

    if not df_amortizacion.empty:

        intereses_capitalizados = (
            df_amortizacion["Interés capitalizado"].sum()
        )

    saldo_despues_gracia = (
        monto_financiado + intereses_capitalizados
    )

    # --------------------------------------------------
    # EVALUACIÓN DEL PROYECTO
    # --------------------------------------------------

    resultados = evaluar_proyecto(
        monto_proyecto=monto_proyecto,
        aporte_propio=aporte_propio,
        flujo_operativo=flujo_operativo,
        horizonte_meses=horizonte_meses,
        mes_inicio_operaciones=mes_inicio_operaciones,
        tasa_descuento=tasa_descuento,
        df_amortizacion=df_amortizacion,
        frecuencia_meses=frecuencia_meses
    )

    # --------------------------------------------------
    # RESULTADOS DE LA EVALUACIÓN
    # --------------------------------------------------

    tasa_descuento_decimal = (
        resultados[
            "tasa_descuento_decimal"
        ]
    )

    tasa_descuento_mensual = (
        resultados[
            "tasa_descuento_mensual"
        ]
    )

    flujo_economico = (
        resultados[
            "flujo_economico"
        ]
    )

    flujo_financiero = (
        resultados[
            "flujo_financiero"
        ]
    )

    flujo_acumulado_economico = (
        resultados[
            "flujo_acumulado_economico"
        ]
    )

    flujo_acumulado_financiero = (
        resultados[
            "flujo_acumulado_financiero"
        ]
    )

    van_economico = (
        resultados[
            "van_economico"
        ]
    )

    van_financiero = (
        resultados[
            "van_financiero"
        ]
    )

    tir_economica_anual = (
        resultados[
            "tir_economica_anual"
        ]
    )

    tir_financiera_anual = (
        resultados[
            "tir_financiera_anual"
        ]
    )

    mes_recuperacion_economica = (
        resultados[
            "mes_recuperacion_economica"
        ]
    )

    mes_recuperacion_financiera = (
        resultados[
            "mes_recuperacion_financiera"
        ]
    )

    df_flujo = (
        resultados[
            "df_flujo"
        ]
    )

    # --------------------------------------------------
    # DATAFRAME RESUMEN PARA EXCEL
    # --------------------------------------------------

    df_resumen = pd.DataFrame(
        {
            "Concepto": [
                "Inversión total",
                "Monto financiado",
                "Aporte propio",
                "Tasa efectiva anual financiamiento",
                "Plazo financiamiento (meses)",
                "Frecuencia de pago",
                "Sistema de amortización",
                "Tipo de gracia",
                "Período de gracia (meses)",
                "Inicio de operaciones",
                "Horizonte del proyecto (meses)",
                "Ingresos mensuales",
                "Costos fijos mensuales",
                "Costos variables mensuales",
                "Flujo operativo mensual",
                "Tasa de descuento anual",
                "VAN económico",
                "TIR económica anual",
                "Recuperación económica (mes)",
                "VAN financiero",
                "TIR financiera anual",
                "Recuperación financiera (mes)"
            ],
            "Valor": [
                monto_proyecto,
                monto_financiado,
                aporte_propio,
                tasa_interes / 100,
                plazo_credito_meses,
                frecuencia_pago,
                tipo_amortizacion,
                tipo_gracia,
                meses_gracia_calculo,
                mes_inicio_operaciones,
                horizonte_meses,
                ingresos,
                costos_fijos,
                costos_variables,
                flujo_operativo,
                tasa_descuento / 100,
                van_economico,
                tir_economica_anual,
                mes_recuperacion_economica,
                van_financiero,
                tir_financiera_anual,
                mes_recuperacion_financiera
            ]
        }
    )

    # --------------------------------------------------
    # GENERAR ARCHIVO EXCEL
    # --------------------------------------------------

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="xlsxwriter"
    ) as writer:

        # --------------------------------------------------
        # OBJETOS DEL LIBRO
        # --------------------------------------------------

        workbook = writer.book

        # --------------------------------------------------
        # EXPORTAR DATAFRAMES
        # --------------------------------------------------
        hoja_resumen = workbook.add_worksheet("Resumen")
        writer.sheets["Resumen"] = hoja_resumen

        df_amortizacion.to_excel(
            writer,
            sheet_name="Amortizacion",
            index=False,
            startrow=2
        )

        df_flujo.to_excel(
            writer,
            sheet_name="Flujo_Caja",
            index=False,
            startrow=2
        )



        hoja_resumen = writer.sheets["Resumen"]
        hoja_amortizacion = writer.sheets["Amortizacion"]
        hoja_flujo = writer.sheets["Flujo_Caja"]

        # --------------------------------------------------
        # FORMATOS GENERALES
        # --------------------------------------------------

        formato_titulo = workbook.add_format(
            {
                "bold": True,
                "font_size": 16,
                "font_color": "white",
                "bg_color": "#1F4E78",
                "align": "left",
                "valign": "vcenter"
            }
        )

        formato_encabezado = workbook.add_format(
            {
                "bold": True,
                "font_color": "white",
                "bg_color": "#4472C4",
                "border": 1,
                "align": "center",
                "valign": "vcenter"
            }
        )

        formato_moneda = workbook.add_format(
            {
                "num_format": '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_porcentaje = workbook.add_format(
            {
                "num_format": '0.00%;[Red](0.00%);-'
            }
        )

        formato_numero = workbook.add_format(
            {
                "num_format": '#,##0.00;[Red](#,##0.00);-'
            }
        )

        formato_entero = workbook.add_format(
            {
                "num_format": '0;[Red](0);-'
            }
        )

        formato_texto = workbook.add_format(
            {
                "align": "left",
                "valign": "vcenter"
            }
        )

        formato_resaltado = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#D9EAF7"
            }
        )

        formato_seccion = workbook.add_format(
            {
                "bold": True,
                "font_color": "white",
                "bg_color": "#5B9BD5",
                "font_size": 11,
                "align": "left",
                "valign": "vcenter"
            }
        )

        formato_concepto = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#EAF2F8"
            }
        )

        formato_valor = workbook.add_format(
            {
                "border": 1
            }
        )

        formato_valor_moneda = workbook.add_format(
            {
                "border": 1,
                "num_format": '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_valor_porcentaje = workbook.add_format(
            {
                "border": 1,
                "num_format": '0.00%'
            }
        )

        formato_indicador = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#D9EAF7",
                "font_size": 11
            }
        )

        formato_indicador_moneda = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#D9EAF7",
                "num_format": '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_indicador_porcentaje = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#D9EAF7",
                "num_format": '0.00%'
            }
        )

        formato_verde_moneda = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#C6EFCE",
                "font_color": "#006100",
                "num_format": '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_rojo_moneda = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#FFC7CE",
                "font_color": "#9C0006",
                "num_format": '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_verde_porcentaje = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#C6EFCE",
                "font_color": "#006100",
                "num_format": "0.00%"
            }
        )

        formato_rojo_porcentaje = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#FFC7CE",
                "font_color": "#9C0006",
                "num_format": "0.00%"
            }
        )

        formato_amarillo = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#FFEB9C",
                "font_color": "#9C6500"
            }
        )

        formato_conclusion_verde = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "bg_color": "#E2F0D9",
                "font_color": "#375623",
                "border": 1
            }
        )

        formato_conclusion_amarilla = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "bg_color": "#FFF2CC",
                "font_color": "#7F6000",
                "border": 1
            }
        )

        formato_conclusion_roja = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "bg_color": "#FCE4D6",
                "font_color": "#9C0006",
                "border": 1
            }
        )

        # ==================================================
        # HOJA RESUMEN
        # ==================================================

        hoja_resumen.merge_range(
            "A1:D1",
            "BI-SMARK | Evaluación de Proyecto de Inversión",
            formato_titulo
        )

        hoja_resumen.set_row(0, 28)

        hoja_resumen.set_column("A:A", 34)
        hoja_resumen.set_column("B:B", 20)
        hoja_resumen.set_column("C:C", 34)
        hoja_resumen.set_column("D:D", 20)

        # --------------------------------------------------
        # DATOS DEL PROYECTO
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A3:D3",
            "DATOS DEL PROYECTO",
            formato_seccion
        )

        hoja_resumen.write("A4", "Inversión total", formato_concepto)
        hoja_resumen.write("B4", monto_proyecto, formato_valor_moneda)

        hoja_resumen.write("C4", "Horizonte del proyecto", formato_concepto)
        hoja_resumen.write("D4", horizonte_meses, formato_valor)

        hoja_resumen.write("A5", "Inicio de operaciones", formato_concepto)
        hoja_resumen.write("B5", mes_inicio_operaciones, formato_valor)

        hoja_resumen.write("C5", "Tasa de descuento anual", formato_concepto)
        hoja_resumen.write("D5", tasa_descuento / 100, formato_valor_porcentaje)

        # --------------------------------------------------
        # OPERACIÓN
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A7:D7",
            "OPERACIÓN",
            formato_seccion
        )

        hoja_resumen.write("A8", "Ingresos mensuales", formato_concepto)
        hoja_resumen.write("B8", ingresos, formato_valor_moneda)

        hoja_resumen.write("C8", "Costos fijos mensuales", formato_concepto)
        hoja_resumen.write("D8", costos_fijos, formato_valor_moneda)

        hoja_resumen.write("A9", "Costos variables mensuales", formato_concepto)
        hoja_resumen.write("B9", costos_variables, formato_valor_moneda)

        hoja_resumen.write("C9", "Flujo operativo mensual", formato_concepto)
        hoja_resumen.write("D9", flujo_operativo, formato_valor_moneda)

        # --------------------------------------------------
        # FINANCIAMIENTO
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A11:D11",
            "FINANCIAMIENTO",
            formato_seccion
        )

        hoja_resumen.write("A12", "Monto financiado", formato_concepto)
        hoja_resumen.write("B12", monto_financiado, formato_valor_moneda)

        hoja_resumen.write("C12", "Aporte propio", formato_concepto)
        hoja_resumen.write("D12", aporte_propio, formato_valor_moneda)

        hoja_resumen.write("A13", "Tasa efectiva anual", formato_concepto)
        hoja_resumen.write("B13", tasa_interes / 100, formato_valor_porcentaje)

        hoja_resumen.write("C13", "Plazo financiamiento", formato_concepto)
        hoja_resumen.write("D13", plazo_credito_meses, formato_valor)

        hoja_resumen.write("A14", "Frecuencia", formato_concepto)
        hoja_resumen.write("B14", frecuencia_pago, formato_valor)

        hoja_resumen.write("C14", "Sistema de amortización", formato_concepto)
        hoja_resumen.write("D14", tipo_amortizacion, formato_valor)

        hoja_resumen.write("A15", "Tipo de gracia", formato_concepto)
        hoja_resumen.write("B15", tipo_gracia, formato_valor)

        hoja_resumen.write("C15", "Período de gracia", formato_concepto)
        hoja_resumen.write("D15", meses_gracia_calculo, formato_valor)

        if tipo_gracia == "Gracia total" and meses_gracia_calculo > 0:

            hoja_resumen.write(
                "A16",
                "Intereses capitalizados",
                formato_concepto
            )

            hoja_resumen.write(
                "B16",
                intereses_capitalizados,
                formato_valor_moneda
            )

            hoja_resumen.write(
                "C16",
                "Saldo después de gracia",
                formato_concepto
            )

            hoja_resumen.write(
                "D16",
                saldo_despues_gracia,
                formato_valor_moneda
            )

        # --------------------------------------------------
        # EVALUACIÓN ECONÓMICA
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A18:D18",
            "EVALUACIÓN ECONÓMICA",
            formato_seccion
        )

        hoja_resumen.write("A19", "VAN económico", formato_indicador)
        if van_economico > 0:
            formato_van_economico = formato_verde_moneda
        else:
            formato_van_economico = formato_rojo_moneda

        hoja_resumen.write(
            "B19",
            van_economico,
            formato_van_economico
        )

        hoja_resumen.write("C19", "TIR económica anual", formato_indicador)

        if tir_economica_anual is not None:

            if tir_economica_anual > tasa_descuento_decimal:
                formato_tir_economica = formato_verde_porcentaje
            else:
                formato_tir_economica = formato_rojo_porcentaje

            hoja_resumen.write(
                "D19",
                tir_economica_anual,
                formato_tir_economica
            )

        else:

            hoja_resumen.write(
                "D19",
                "No calculable",
                formato_amarillo
            )

        hoja_resumen.write(
            "A20",
            "Recuperación simple",
            formato_indicador
        )

        if mes_recuperacion_economica is not None:
            hoja_resumen.write(
                "B20",
                mes_recuperacion_economica,
                formato_indicador
            )
        else:
            hoja_resumen.write(
                "B20",
                "No se recupera",
                formato_indicador
            )

        # --------------------------------------------------
        # EVALUACIÓN FINANCIERA
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A22:D22",
            "EVALUACIÓN FINANCIERA DEL INVERSIONISTA",
            formato_seccion
        )

        hoja_resumen.write("A23", "VAN financiero", formato_indicador)
        if van_financiero > 0:
            formato_van_financiero = formato_verde_moneda
        else:
            formato_van_financiero = formato_rojo_moneda

        hoja_resumen.write(
            "B23",
            van_financiero,
            formato_van_financiero
        )

        hoja_resumen.write(
            "C23",
            "TIR financiera anual",
            formato_indicador
        )

        if tir_financiera_anual is not None:

            if tir_financiera_anual > tasa_descuento_decimal:
                formato_tir_financiera = formato_verde_porcentaje
            else:
                formato_tir_financiera = formato_rojo_porcentaje

            hoja_resumen.write(
                "D23",
                tir_financiera_anual,
                formato_tir_financiera
            )

        else:

            hoja_resumen.write(
                "D23",
                "No calculable",
                formato_amarillo
            )

        hoja_resumen.write(
            "A24",
            "Recuperación aporte propio",
            formato_indicador
        )

        if mes_recuperacion_financiera == "No aplica":

            hoja_resumen.write(
                "B24",
                "No aplica",
                formato_indicador
            )

        elif mes_recuperacion_financiera is not None:

            hoja_resumen.write(
                "B24",
                mes_recuperacion_financiera,
                formato_indicador
            )

        else:

            hoja_resumen.write(
                "B24",
                "No se recupera",
                formato_indicador
            )
        # --------------------------------------------------
        # CONCLUSIÓN EJECUTIVA
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A26:D26",
            "CONCLUSIÓN EJECUTIVA",
            formato_seccion
        )

        cumple_van_economico = (
            van_economico > 0
        )

        cumple_tir_economica = (
            tir_economica_anual is not None
            and tir_economica_anual > tasa_descuento_decimal
        )

        cumple_van_financiero = (
            van_financiero > 0
        )

        cumple_tir_financiera = (
            tir_financiera_anual is not None
            and tir_financiera_anual > tasa_descuento_decimal
        )

        criterios_cumplidos = sum(
            [
                cumple_van_economico,
                cumple_tir_economica,
                cumple_van_financiero,
                cumple_tir_financiera
            ]
        )

        if criterios_cumplidos == 4:

            conclusion = (
                "Bajo los supuestos ingresados, el proyecto presenta "
                "resultados favorables tanto desde la perspectiva "
                "económica como desde la perspectiva financiera del "
                "inversionista. El VAN es positivo y la TIR supera "
                "la tasa mínima requerida en ambas evaluaciones."
            )

            formato_conclusion = (
                formato_conclusion_verde
            )

        elif criterios_cumplidos >= 2:

            conclusion = (
                "Los resultados del proyecto son mixtos. Algunos "
                "indicadores cumplen los criterios de rentabilidad, "
                "mientras que otros no alcanzan la tasa mínima "
                "requerida o presentan un VAN no favorable. "
                "Se recomienda revisar los supuestos y analizar "
                "la estructura económica y financiera por separado."
            )

            formato_conclusion = (
                formato_conclusion_amarilla
            )

        else:

            conclusion = (
                "Bajo los supuestos ingresados, el proyecto no "
                "presenta resultados suficientes para alcanzar "
                "los criterios mínimos de rentabilidad evaluados. "
                "Se recomienda revisar inversión, ingresos, costos, "
                "financiamiento y horizonte antes de tomar una decisión."
            )

            formato_conclusion = (
                formato_conclusion_roja
            )

        hoja_resumen.merge_range(
            "A27:D29",
            conclusion,
            formato_conclusion
        )

        hoja_resumen.set_row(
            26,
            32
        )

        hoja_resumen.set_row(
            27,
            24
        )

        hoja_resumen.set_row(
            28,
            24
        )

        hoja_resumen.freeze_panes(3, 0)

        # ==================================================
        # HOJA AMORTIZACION
        # ==================================================

        hoja_amortizacion.merge_range(
            "A1:I1",
            (
                "BI-SMARK | Tabla de Amortización - "
                f"Sistema {tipo_amortizacion}"
            ),
            formato_titulo
        )

        hoja_amortizacion.set_row(
            0,
            26
        )

        columnas_amortizacion = list(
            df_amortizacion.columns
        )

        for columna, nombre in enumerate(
            columnas_amortizacion
        ):

            hoja_amortizacion.write(
                2,
                columna,
                nombre,
                formato_encabezado
            )

        hoja_amortizacion.freeze_panes(
            3,
            2
        )

        hoja_amortizacion.set_column(
            "A:A",
            10
        )

        hoja_amortizacion.set_column(
            "B:B",
            18
        )

        hoja_amortizacion.set_column(
            "C:I",
            18,
            formato_moneda
        )

        # ==================================================
        # HOJA FLUJO DE CAJA
        # ==================================================

        hoja_flujo.merge_range(
            "A1:F1",
            "BI-SMARK | Flujo de Caja Proyectado",
            formato_titulo
        )

        hoja_flujo.set_row(
            0,
            26
        )

        columnas_flujo = list(
            df_flujo.columns
        )

        for columna, nombre in enumerate(
            columnas_flujo
        ):

            hoja_flujo.write(
                2,
                columna,
                nombre,
                formato_encabezado
            )

        hoja_flujo.freeze_panes(
            3,
            2
        )

        hoja_flujo.set_column(
            "A:A",
            10,
            formato_entero
        )

        hoja_flujo.set_column(
            "B:B",
            18,
            formato_texto
        )

        hoja_flujo.set_column(
            "C:F",
            22,
            formato_moneda
        )

        # --------------------------------------------------
        # GRÁFICO DE FLUJO ACUMULADO
        # --------------------------------------------------

        grafico_flujo = workbook.add_chart(
            {
                "type": "line"
            }
        )

        ultima_fila_flujo = (
            len(df_flujo) + 2
        )

        # Flujo acumulado económico

        grafico_flujo.add_series(
            {
                "name": "Acumulado económico",
                "categories": [
                    "Flujo_Caja",
                    3,
                    0,
                    ultima_fila_flujo,
                    0
                ],
                "values": [
                    "Flujo_Caja",
                    3,
                    3,
                    ultima_fila_flujo,
                    3
                ]
            }
        )

        # Flujo acumulado financiero

        grafico_flujo.add_series(
            {
                "name": "Acumulado financiero",
                "categories": [
                    "Flujo_Caja",
                    3,
                    0,
                    ultima_fila_flujo,
                    0
                ],
                "values": [
                    "Flujo_Caja",
                    3,
                    5,
                    ultima_fila_flujo,
                    5
                ]
            }
        )

        grafico_flujo.set_title(
            {
                "name": "Evolución del flujo acumulado"
            }
        )

        grafico_flujo.set_x_axis(
            {
                "name": "Mes"
            }
        )

        grafico_flujo.set_y_axis(
            {
                "name": "Valor acumulado ($)",
                "num_format": '$#,##0'
            }
        )

        grafico_flujo.set_legend(
            {
                "position": "bottom"
            }
        )

        grafico_flujo.set_size(
            {
                "width": 760,
                "height": 420
            }
        )

        hoja_flujo.insert_chart(
            "H3",
            grafico_flujo
        )

        # --------------------------------------------------
        # PRESENTACIÓN GENERAL
        # --------------------------------------------------

        hoja_resumen.hide_gridlines(2)
        hoja_amortizacion.hide_gridlines(2)
        hoja_flujo.hide_gridlines(2)

    # --------------------------------------------------
    # RESULTADOS GENERALES
    # --------------------------------------------------

    st.divider()

    st.subheader("Resumen del proyecto")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Inversión total",
        f"${monto_proyecto:,.2f}"
    )

    col2.metric(
        "Financiamiento",
        f"${monto_financiado:,.2f}"
    )

    col3.metric(
        "Aporte propio",
        f"${aporte_propio:,.2f}"
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Ingresos mensuales",
        f"${ingresos:,.2f}"
    )

    col5.metric(
        "Costos mensuales",
        f"${costos_fijos + costos_variables:,.2f}"
    )

    col6.metric(
        "Flujo operativo mensual",
        f"${flujo_operativo:,.2f}"
    )

    col_plazo1, col_plazo2 = st.columns(2)

    col_plazo1.metric(
        "Plazo del financiamiento",
        f"{plazo_credito_meses} meses"
    )

    col_plazo2.metric(
        "Horizonte del proyecto",
        f"{horizonte_meses} meses"
    )

    col_inicio, col_operacion = st.columns(2)

    col_inicio.metric(
        "Inicio de operaciones",
        f"Mes {mes_inicio_operaciones}"
    )

    meses_operacion = (
        horizonte_meses
        - mes_inicio_operaciones
        + 1
    )

    col_operacion.metric(
        "Meses operativos evaluados",
        meses_operacion
    )
    # --------------------------------------------------
    # RESULTADOS DEL FINANCIAMIENTO
    # --------------------------------------------------

    st.subheader("Financiamiento")

    col7, col8, col9 = st.columns(3)

    col7.metric(
        "Número de pagos",
        numero_pagos
    )

    col8.metric(
        "Tasa por período",
        f"{tasa_periodica * 100:.4f}%"
    )

    col9.metric(
        "Frecuencia",
        frecuencia_pago
    )

    gracia1, gracia2 = st.columns(2)

    gracia1.metric(
        "Tipo de gracia",
        tipo_gracia
    )

    gracia2.metric(
        "Período de gracia",
        f"{meses_gracia_calculo} meses"
    )

    if tipo_gracia == "Gracia total" and meses_gracia_calculo > 0:

        gracia3, gracia4 = st.columns(2)

        gracia3.metric(
            "Intereses capitalizados",
            f"${intereses_capitalizados:,.2f}"
        )

        gracia4.metric(
            "Saldo después de la gracia",
            f"${saldo_despues_gracia:,.2f}"
        )

    if monto_financiado > 0 and not df_amortizacion.empty:

        total_intereses = (
            df_amortizacion["Interés"].sum()
        )

        total_pagado = (
            df_amortizacion["Cuota"].sum()
        )

        col10, col11 = st.columns(2)

        col10.metric(
            "Total intereses",
            f"${total_intereses:,.2f}"
        )

        col11.metric(
            "Total pagado al banco",
            f"${total_pagado:,.2f}"
        )

        st.subheader(
            f"Tabla de amortización - Sistema {tipo_amortizacion}"
        )

        st.dataframe(
            df_amortizacion.style.format(
                {
                    "Saldo inicial": "${:,.2f}",
                    "Interés": "${:,.2f}",
                    "Interés pagado": "${:,.2f}",
                    "Interés capitalizado": "${:,.2f}",
                    "Amortización": "${:,.2f}",
                    "Cuota": "${:,.2f}",
                    "Saldo final": "${:,.2f}"
                }
            ),
            use_container_width=True
        )

    else:

        st.info(
            "El proyecto no tiene financiamiento externo."
        )
    # --------------------------------------------------
    # EVALUACIÓN DEL PROYECTO
    # --------------------------------------------------

    st.divider()

    st.header("Evaluación del proyecto")

    st.caption(
        "Resultados simplificados sin impuestos, depreciaciones, "
        "inflación ni valor residual."
    )

    # --------------------------------------------------
    # EVALUACIÓN ECONÓMICA
    # --------------------------------------------------

    st.subheader("Evaluación económica")

    st.write(
        "Analiza la rentabilidad del proyecto "
        "independientemente de su financiamiento."
    )

    eco1, eco2, eco3 = st.columns(3)

    eco1.metric(
        "VAN económico",
        f"${van_economico:,.2f}"
    )

    if tir_economica_anual is not None:

        eco2.metric(
            "TIR económica anual",
            f"{tir_economica_anual * 100:.2f}%"
        )

    else:

        eco2.metric(
            "TIR económica anual",
            "No calculable"
        )

    if mes_recuperacion_economica is not None:

        eco3.metric(
            "Recuperación simple",
            f"Mes {mes_recuperacion_economica}"
        )

    else:

        eco3.metric(
            "Recuperación simple",
            "No se recupera"
        )

    # --------------------------------------------------
    # INTERPRETACIÓN ECONÓMICA
    # --------------------------------------------------

    if (
        van_economico > 0
        and tir_economica_anual is not None
        and tir_economica_anual > tasa_descuento_decimal
    ):

        st.success(
            "El proyecto es económicamente rentable bajo "
            "los supuestos ingresados. El VAN es positivo "
            "y la TIR supera la tasa mínima requerida."
        )

    elif van_economico > 0:

        st.success(
            "El proyecto presenta un VAN económico positivo."
        )

    else:

        st.warning(
            "El proyecto no alcanza la rentabilidad mínima "
            "requerida bajo los supuestos ingresados."
        )

    # --------------------------------------------------
    # EVALUACIÓN FINANCIERA
    # --------------------------------------------------

    st.subheader("Evaluación financiera del inversionista")

    st.write(
        "Considera el aporte propio y los pagos "
        "del financiamiento."
    )

    fin1, fin2, fin3 = st.columns(3)

    fin1.metric(
        "VAN financiero",
        f"${van_financiero:,.2f}"
    )

    if tir_financiera_anual is not None:

        fin2.metric(
            "TIR financiera anual",
            f"{tir_financiera_anual * 100:.2f}%"
        )

    else:

        fin2.metric(
            "TIR financiera anual",
            "No calculable"
        )

    if mes_recuperacion_financiera == "No aplica":

        fin3.metric(
            "Recuperación del aporte propio",
            "No aplica"
        )

    elif mes_recuperacion_financiera is not None:

        fin3.metric(
            "Recuperación del aporte propio",
            f"Mes {mes_recuperacion_financiera}"
        )

    else:

        fin3.metric(
            "Recuperación del aporte propio",
            "No se recupera"
        )

    # --------------------------------------------------
    # TABLA DE FLUJO DE CAJA
    # --------------------------------------------------

    st.subheader("Flujo de caja proyectado")

    st.dataframe(
        df_flujo.style.format(
            {
                "Flujo económico": "${:,.2f}",
                "Acumulado económico": "${:,.2f}",
                "Flujo financiero": "${:,.2f}",
                "Acumulado financiero": "${:,.2f}"
            }
        ),
        use_container_width=True
    )

    st.divider()

    st.subheader("Descargar resultados")

    st.download_button(
        label="📥 Descargar análisis en Excel",
        data=excel_buffer.getvalue(),
        file_name="evaluacion_proyecto_bi_smark.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )