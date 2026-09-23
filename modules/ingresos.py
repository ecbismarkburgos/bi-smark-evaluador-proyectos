import pandas as pd


def generar_ingresos(
    productos,
    horizonte_meses
):

    # Mes 0 no genera ingresos
    ingresos_totales = [
        0.0
        for _ in range(horizonte_meses + 1)
    ]

    detalle = {
        "Mes": list(
            range(0, horizonte_meses + 1)
        )
    }

    for producto in productos:

        nombre = producto["nombre"]

        precio = producto[
            "precio_unitario"
        ]

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

        ingresos_producto = [
            0.0
            for _ in range(
                horizonte_meses + 1
            )
        ]

        ingreso_base = (
            precio * unidades
        )

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

                ingreso_mes = (
                    ingreso_base
                    * factor_crecimiento
                )

                ingresos_producto[
                    mes
                ] = ingreso_mes

                ingresos_totales[
                    mes
                ] += ingreso_mes

        detalle[nombre] = (
            ingresos_producto
        )

    detalle[
        "Ingresos totales"
    ] = ingresos_totales

    df_ingresos = pd.DataFrame(
        detalle
    )

    return (
        ingresos_totales,
        df_ingresos
    )
