import pandas as pd


def generar_amortizacion(
    monto_financiado,
    tasa_periodica,
    numero_pagos,
    periodos_gracia,
    tipo_gracia,
    tipo_amortizacion
):

    tabla_amortizacion = []

    saldo = monto_financiado

    periodos_amortizacion = (
        numero_pagos - periodos_gracia
    )

    if monto_financiado > 0:

        # ==============================================
        # ETAPA DE GRACIA
        # ==============================================

        for periodo in range(
            1,
            periodos_gracia + 1
        ):

            saldo_inicial = saldo

            interes = (
                saldo_inicial
                * tasa_periodica
            )

            # ------------------------------------------
            # GRACIA DE CAPITAL
            # ------------------------------------------

            if tipo_gracia == "Gracia de capital":

                amortizacion = 0

                cuota = interes

                saldo_final = saldo_inicial

                interes_pagado = interes

                interes_capitalizado = 0

            # ------------------------------------------
            # GRACIA TOTAL
            # ------------------------------------------

            elif tipo_gracia == "Gracia total":

                amortizacion = 0

                cuota = 0

                interes_pagado = 0

                interes_capitalizado = interes

                saldo_final = (
                    saldo_inicial
                    + interes
                )

            else:

                amortizacion = 0

                cuota = 0

                interes_pagado = 0

                interes_capitalizado = 0

                saldo_final = saldo_inicial

            tabla_amortizacion.append(
                {
                    "Periodo": periodo,
                    "Etapa": "Gracia",
                    "Saldo inicial": saldo_inicial,
                    "Interés": interes,
                    "Interés pagado": interes_pagado,
                    "Interés capitalizado": interes_capitalizado,
                    "Amortización": amortizacion,
                    "Cuota": cuota,
                    "Saldo final": saldo_final
                }
            )

            saldo = saldo_final

        # ==============================================
        # SISTEMA FRANCÉS
        # ==============================================

        if tipo_amortizacion == "Francés":

            if tasa_periodica == 0:

                cuota = (
                    saldo
                    / periodos_amortizacion
                )

            else:

                cuota = (
                    saldo
                    * (
                        tasa_periodica
                        * (1 + tasa_periodica)
                        ** periodos_amortizacion
                    )
                    / (
                        (1 + tasa_periodica)
                        ** periodos_amortizacion
                        - 1
                    )
                )

            for numero in range(
                1,
                periodos_amortizacion + 1
            ):

                periodo = (
                    periodos_gracia
                    + numero
                )

                saldo_inicial = saldo

                interes = (
                    saldo_inicial
                    * tasa_periodica
                )

                interes_pagado = interes

                interes_capitalizado = 0

                amortizacion = (
                    cuota - interes
                )

                saldo_final = (
                    saldo_inicial
                    - amortizacion
                )

                # Ajuste final para evitar
                # residuos por redondeo

                if numero == periodos_amortizacion:

                    amortizacion = (
                        saldo_inicial
                    )

                    cuota = (
                        amortizacion
                        + interes
                    )

                    saldo_final = 0

                elif saldo_final < 0.01:

                    saldo_final = 0

                tabla_amortizacion.append(
                    {
                        "Periodo": periodo,
                        "Etapa": "Amortización",
                        "Saldo inicial": saldo_inicial,
                        "Interés": interes,
                        "Interés pagado": interes_pagado,
                        "Interés capitalizado": interes_capitalizado,
                        "Amortización": amortizacion,
                        "Cuota": cuota,
                        "Saldo final": saldo_final
                    }
                )

                saldo = saldo_final

        # ==============================================
        # SISTEMA ALEMÁN
        # ==============================================

        elif tipo_amortizacion == "Alemán":

            amortizacion_constante = (
                saldo
                / periodos_amortizacion
            )

            for numero in range(
                1,
                periodos_amortizacion + 1
            ):

                periodo = (
                    periodos_gracia
                    + numero
                )

                saldo_inicial = saldo

                interes = (
                    saldo_inicial
                    * tasa_periodica
                )

                interes_pagado = interes

                interes_capitalizado = 0

                if numero == periodos_amortizacion:

                    amortizacion = saldo_inicial

                else:

                    amortizacion = (
                        amortizacion_constante
                    )

                cuota = (
                    amortizacion
                    + interes
                )

                saldo_final = (
                    saldo_inicial
                    - amortizacion
                )

                if saldo_final < 0.01:
                    saldo_final = 0

                tabla_amortizacion.append(
                    {
                        "Periodo": periodo,
                        "Etapa": "Amortización",
                        "Saldo inicial": saldo_inicial,
                        "Interés": interes,
                        "Interés pagado": interes_pagado,
                        "Interés capitalizado": interes_capitalizado,
                        "Amortización": amortizacion,
                        "Cuota": cuota,
                        "Saldo final": saldo_final
                    }
                )

                saldo = saldo_final

    columnas = [
        "Periodo",
        "Etapa",
        "Saldo inicial",
        "Interés",
        "Interés pagado",
        "Interés capitalizado",
        "Amortización",
        "Cuota",
        "Saldo final"
    ]

    df_amortizacion = pd.DataFrame(
        tabla_amortizacion,
        columns=columnas
    )

    return df_amortizacion