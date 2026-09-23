import pandas as pd


def generar_costos(
    productos,
    costos_fijos_detalle,
    nomina_mensual,
    costos_variables_unitarios,
    horizonte_meses,
    mes_inicio_operaciones
):

    costos_totales = [
        0.0
        for _ in range(
            horizonte_meses + 1
        )
    ]

    costos_fijos_mensuales = [
        0.0
        for _ in range(
            horizonte_meses + 1
        )
    ]

    nomina_mensual_proyectada = [
        0.0
        for _ in range(
            horizonte_meses + 1
        )
    ]

    costos_variables_totales = [
        0.0
        for _ in range(
            horizonte_meses + 1
        )
    ]

    total_costos_fijos = sum(
        costo["monto"]
        for costo in costos_fijos_detalle
    )

    detalle = {
        "Mes": list(
            range(
                0,
                horizonte_meses + 1
            )
        )
    }

    # --------------------------------------------------
    # COSTOS FIJOS Y NÓMINA
    # --------------------------------------------------

    for mes in range(
        1,
        horizonte_meses + 1
    ):

        if mes >= mes_inicio_operaciones:

            costos_fijos_mensuales[
                mes
            ] = total_costos_fijos

            nomina_mensual_proyectada[
                mes
            ] = nomina_mensual

    # --------------------------------------------------
    # COSTOS VARIABLES POR PRODUCTO
    # --------------------------------------------------

    for i, producto in enumerate(
        productos
    ):

        nombre = producto["nombre"]

        unidades = producto[
            "unidades_mensuales"
        ]

        mes_inicio = producto[
            "mes_inicio"
        ]

        crecimiento_anual = (
            producto[
                "crecimiento_anual"
            ] / 100
        )

        costo_unitario = (
            costos_variables_unitarios[i]
        )

        costo_producto = [
            0.0
            for _ in range(
                horizonte_meses + 1
            )
        ]

        for mes in range(
            1,
            horizonte_meses + 1
        ):

            if mes >= mes_inicio:

                meses_transcurridos = (
                    mes - mes_inicio
                )

                factor_crecimiento = (
                    (1 + crecimiento_anual)
                    ** (
                        meses_transcurridos
                        / 12
                    )
                )

                unidades_mes = (
                    unidades
                    * factor_crecimiento
                )

                costo_mes = (
                    unidades_mes
                    * costo_unitario
                )

                costo_producto[
                    mes
                ] = costo_mes

                costos_variables_totales[
                    mes
                ] += costo_mes

        detalle[
            f"Variable - {nombre}"
        ] = costo_producto

    # --------------------------------------------------
    # COSTOS TOTALES
    # --------------------------------------------------

    for mes in range(
        0,
        horizonte_meses + 1
    ):

        costos_totales[mes] = (
            costos_fijos_mensuales[mes]
            + nomina_mensual_proyectada[mes]
            + costos_variables_totales[mes]
        )

    detalle[
        "Costos fijos"
    ] = costos_fijos_mensuales

    detalle[
        "Nómina"
    ] = nomina_mensual_proyectada

    detalle[
        "Costos variables"
    ] = costos_variables_totales

    detalle[
        "Costos totales"
    ] = costos_totales

    df_costos = pd.DataFrame(
        detalle
    )

    return (
        costos_totales,
        costos_fijos_mensuales,
        costos_variables_totales,
        nomina_mensual_proyectada,
        df_costos
    )
