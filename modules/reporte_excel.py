from io import BytesIO

import pandas as pd


def generar_reporte_excel(
    datos,
    resultados,
    df_amortizacion,
    df_flujo
):

    # --------------------------------------------------
    # DATOS DEL PROYECTO
    # --------------------------------------------------

    monto_proyecto = datos["monto_proyecto"]
    monto_financiado = datos["monto_financiado"]
    aporte_propio = datos["aporte_propio"]

    tasa_interes = datos["tasa_interes"]
    plazo_credito_meses = datos["plazo_credito_meses"]

    frecuencia_pago = datos["frecuencia_pago"]
    tipo_amortizacion = datos["tipo_amortizacion"]

    tipo_gracia = datos["tipo_gracia"]
    meses_gracia_calculo = datos["meses_gracia_calculo"]

    mes_inicio_operaciones = datos[
        "mes_inicio_operaciones"
    ]

    horizonte_meses = datos["horizonte_meses"]

    ingresos = datos["ingresos"]
    costos_fijos = datos["costos_fijos"]
    costos_variables = datos["costos_variables"]

    flujo_operativo = datos["flujo_operativo"]

    tasa_descuento = datos["tasa_descuento"]

    intereses_capitalizados = datos[
        "intereses_capitalizados"
    ]

    saldo_despues_gracia = datos[
        "saldo_despues_gracia"
    ]

    # --------------------------------------------------
    # RESULTADOS FINANCIEROS
    # --------------------------------------------------

    van_economico = resultados[
        "van_economico"
    ]

    van_financiero = resultados[
        "van_financiero"
    ]

    tir_economica_anual = resultados[
        "tir_economica_anual"
    ]

    tir_financiera_anual = resultados[
        "tir_financiera_anual"
    ]

    mes_recuperacion_economica = resultados[
        "mes_recuperacion_economica"
    ]

    mes_recuperacion_financiera = resultados[
        "mes_recuperacion_financiera"
    ]

    tasa_descuento_decimal = resultados[
        "tasa_descuento_decimal"
    ]

    # --------------------------------------------------
    # CREAR ARCHIVO
    # --------------------------------------------------

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        # --------------------------------------------------
        # CREAR HOJAS
        # --------------------------------------------------

        hoja_resumen = workbook.add_worksheet(
            "Resumen"
        )

        writer.sheets["Resumen"] = (
            hoja_resumen
        )

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

        hoja_amortizacion = writer.sheets[
            "Amortizacion"
        ]

        hoja_flujo = writer.sheets[
            "Flujo_Caja"
        ]

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
                "num_format":
                    '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_entero = workbook.add_format(
            {
                "num_format":
                    '0;[Red](0);-'
            }
        )

        formato_texto = workbook.add_format(
            {
                "align": "left",
                "valign": "vcenter"
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

        formato_valor_moneda = (
            workbook.add_format(
                {
                    "border": 1,
                    "num_format":
                        '$#,##0.00;[Red]($#,##0.00);-'
                }
            )
        )

        formato_valor_porcentaje = (
            workbook.add_format(
                {
                    "border": 1,
                    "num_format": "0.00%"
                }
            )
        )

        formato_indicador = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#D9EAF7",
                "font_size": 11
            }
        )

        formato_verde_moneda = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#C6EFCE",
                "font_color": "#006100",
                "num_format":
                    '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_rojo_moneda = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#FFC7CE",
                "font_color": "#9C0006",
                "num_format":
                    '$#,##0.00;[Red]($#,##0.00);-'
            }
        )

        formato_verde_porcentaje = (
            workbook.add_format(
                {
                    "bold": True,
                    "border": 1,
                    "bg_color": "#C6EFCE",
                    "font_color": "#006100",
                    "num_format": "0.00%"
                }
            )
        )

        formato_rojo_porcentaje = (
            workbook.add_format(
                {
                    "bold": True,
                    "border": 1,
                    "bg_color": "#FFC7CE",
                    "font_color": "#9C0006",
                    "num_format": "0.00%"
                }
            )
        )

        formato_amarillo = workbook.add_format(
            {
                "bold": True,
                "border": 1,
                "bg_color": "#FFEB9C",
                "font_color": "#9C6500"
            }
        )

        formato_conclusion_verde = (
            workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "top",
                    "bg_color": "#E2F0D9",
                    "font_color": "#375623",
                    "border": 1
                }
            )
        )

        formato_conclusion_amarilla = (
            workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "top",
                    "bg_color": "#FFF2CC",
                    "font_color": "#7F6000",
                    "border": 1
                }
            )
        )

        formato_conclusion_roja = (
            workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "top",
                    "bg_color": "#FCE4D6",
                    "font_color": "#9C0006",
                    "border": 1
                }
            )
        )

        # ==================================================
        # HOJA RESUMEN
        # ==================================================

        hoja_resumen.merge_range(
            "A1:D1",
            (
                "BI-SMARK | Evaluación de "
                "Proyecto de Inversión"
            ),
            formato_titulo
        )

        hoja_resumen.set_row(
            0,
            28
        )

        hoja_resumen.set_column(
            "A:A",
            34
        )

        hoja_resumen.set_column(
            "B:B",
            20
        )

        hoja_resumen.set_column(
            "C:C",
            34
        )

        hoja_resumen.set_column(
            "D:D",
            20
        )

        # --------------------------------------------------
        # DATOS DEL PROYECTO
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A3:D3",
            "DATOS DEL PROYECTO",
            formato_seccion
        )

        hoja_resumen.write(
            "A4",
            "Inversión total",
            formato_concepto
        )

        hoja_resumen.write(
            "B4",
            monto_proyecto,
            formato_valor_moneda
        )

        hoja_resumen.write(
            "C4",
            "Horizonte del proyecto",
            formato_concepto
        )

        hoja_resumen.write(
            "D4",
            horizonte_meses,
            formato_valor
        )

        hoja_resumen.write(
            "A5",
            "Inicio de operaciones",
            formato_concepto
        )

        hoja_resumen.write(
            "B5",
            mes_inicio_operaciones,
            formato_valor
        )

        hoja_resumen.write(
            "C5",
            "Tasa de descuento anual",
            formato_concepto
        )

        hoja_resumen.write(
            "D5",
            tasa_descuento / 100,
            formato_valor_porcentaje
        )

        # --------------------------------------------------
        # OPERACIÓN
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A7:D7",
            "OPERACIÓN",
            formato_seccion
        )

        hoja_resumen.write(
            "A8",
            "Ingresos mensuales",
            formato_concepto
        )

        hoja_resumen.write(
            "B8",
            ingresos,
            formato_valor_moneda
        )

        hoja_resumen.write(
            "C8",
            "Costos fijos mensuales",
            formato_concepto
        )

        hoja_resumen.write(
            "D8",
            costos_fijos,
            formato_valor_moneda
        )

        hoja_resumen.write(
            "A9",
            "Costos variables mensuales",
            formato_concepto
        )

        hoja_resumen.write(
            "B9",
            costos_variables,
            formato_valor_moneda
        )

        hoja_resumen.write(
            "C9",
            "Flujo operativo mensual",
            formato_concepto
        )

        hoja_resumen.write(
            "D9",
            flujo_operativo,
            formato_valor_moneda
        )

        # --------------------------------------------------
        # FINANCIAMIENTO
        # --------------------------------------------------

        hoja_resumen.merge_range(
            "A11:D11",
            "FINANCIAMIENTO",
            formato_seccion
        )

        hoja_resumen.write(
            "A12",
            "Monto financiado",
            formato_concepto
        )

        hoja_resumen.write(
            "B12",
            monto_financiado,
            formato_valor_moneda
        )

        hoja_resumen.write(
            "C12",
            "Aporte propio",
            formato_concepto
        )

        hoja_resumen.write(
            "D12",
            aporte_propio,
            formato_valor_moneda
        )

        hoja_resumen.write(
            "A13",
            "Tasa efectiva anual",
            formato_concepto
        )

        hoja_resumen.write(
            "B13",
            tasa_interes / 100,
            formato_valor_porcentaje
        )

        hoja_resumen.write(
            "C13",
            "Plazo financiamiento",
            formato_concepto
        )

        hoja_resumen.write(
            "D13",
            plazo_credito_meses,
            formato_valor
        )

        hoja_resumen.write(
            "A14",
            "Frecuencia",
            formato_concepto
        )

        hoja_resumen.write(
            "B14",
            frecuencia_pago,
            formato_valor
        )

        hoja_resumen.write(
            "C14",
            "Sistema de amortización",
            formato_concepto
        )

        hoja_resumen.write(
            "D14",
            tipo_amortizacion,
            formato_valor
        )

        hoja_resumen.write(
            "A15",
            "Tipo de gracia",
            formato_concepto
        )

        hoja_resumen.write(
            "B15",
            tipo_gracia,
            formato_valor
        )

        hoja_resumen.write(
            "C15",
            "Período de gracia",
            formato_concepto
        )

        hoja_resumen.write(
            "D15",
            meses_gracia_calculo,
            formato_valor
        )

        if (
            tipo_gracia == "Gracia total"
            and meses_gracia_calculo > 0
        ):

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

        hoja_resumen.write(
            "A19",
            "VAN económico",
            formato_indicador
        )

        if van_economico > 0:

            formato_van_economico = (
                formato_verde_moneda
            )

        else:

            formato_van_economico = (
                formato_rojo_moneda
            )

        hoja_resumen.write(
            "B19",
            van_economico,
            formato_van_economico
        )

        hoja_resumen.write(
            "C19",
            "TIR económica anual",
            formato_indicador
        )

        if tir_economica_anual is not None:

            if (
                tir_economica_anual
                > tasa_descuento_decimal
            ):

                formato_tir_economica = (
                    formato_verde_porcentaje
                )

            else:

                formato_tir_economica = (
                    formato_rojo_porcentaje
                )

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

        if (
            mes_recuperacion_economica
            is not None
        ):

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
            (
                "EVALUACIÓN FINANCIERA "
                "DEL INVERSIONISTA"
            ),
            formato_seccion
        )

        hoja_resumen.write(
            "A23",
            "VAN financiero",
            formato_indicador
        )

        if van_financiero > 0:

            formato_van_financiero = (
                formato_verde_moneda
            )

        else:

            formato_van_financiero = (
                formato_rojo_moneda
            )

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

            if (
                tir_financiera_anual
                > tasa_descuento_decimal
            ):

                formato_tir_financiera = (
                    formato_verde_porcentaje
                )

            else:

                formato_tir_financiera = (
                    formato_rojo_porcentaje
                )

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

        if (
            mes_recuperacion_financiera
            == "No aplica"
        ):

            hoja_resumen.write(
                "B24",
                "No aplica",
                formato_indicador
            )

        elif (
            mes_recuperacion_financiera
            is not None
        ):

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
            and tir_economica_anual
            > tasa_descuento_decimal
        )

        cumple_van_financiero = (
            van_financiero > 0
        )

        cumple_tir_financiera = (
            tir_financiera_anual is not None
            and tir_financiera_anual
            > tasa_descuento_decimal
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
                "Bajo los supuestos ingresados, "
                "el proyecto presenta resultados "
                "favorables tanto desde la "
                "perspectiva económica como desde "
                "la perspectiva financiera del "
                "inversionista. El VAN es positivo "
                "y la TIR supera la tasa mínima "
                "requerida en ambas evaluaciones."
            )

            formato_conclusion = (
                formato_conclusion_verde
            )

        elif criterios_cumplidos >= 2:

            conclusion = (
                "Los resultados del proyecto son "
                "mixtos. Algunos indicadores "
                "cumplen los criterios de "
                "rentabilidad, mientras que otros "
                "no alcanzan la tasa mínima "
                "requerida o presentan un VAN no "
                "favorable. Se recomienda revisar "
                "los supuestos y analizar la "
                "estructura económica y financiera "
                "por separado."
            )

            formato_conclusion = (
                formato_conclusion_amarilla
            )

        else:

            conclusion = (
                "Bajo los supuestos ingresados, "
                "el proyecto no presenta resultados "
                "suficientes para alcanzar los "
                "criterios mínimos de rentabilidad "
                "evaluados. Se recomienda revisar "
                "inversión, ingresos, costos, "
                "financiamiento y horizonte antes "
                "de tomar una decisión."
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

        hoja_resumen.freeze_panes(
            3,
            0
        )

        # ==================================================
        # HOJA AMORTIZACIÓN
        # ==================================================

        hoja_amortizacion.merge_range(
            "A1:I1",
            (
                "BI-SMARK | Tabla de "
                "Amortización - Sistema "
                f"{tipo_amortizacion}"
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
        # GRÁFICO
        # --------------------------------------------------

        grafico_flujo = workbook.add_chart(
            {
                "type": "line"
            }
        )

        ultima_fila_flujo = (
            len(df_flujo) + 2
        )

        grafico_flujo.add_series(
            {
                "name":
                    "Acumulado económico",

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

        grafico_flujo.add_series(
            {
                "name":
                    "Acumulado financiero",

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
                "name":
                    "Evolución del flujo acumulado"
            }
        )

        grafico_flujo.set_x_axis(
            {
                "name": "Mes"
            }
        )

        grafico_flujo.set_y_axis(
            {
                "name":
                    "Valor acumulado ($)",

                "num_format":
                    "$#,##0"
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

    excel_buffer.seek(0)

    return excel_buffer
