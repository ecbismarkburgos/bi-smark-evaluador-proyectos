import pandas as pd
import numpy_financial as npf


def evaluar_proyecto(
    monto_proyecto,
    aporte_propio,
    flujo_operativo,
    horizonte_meses,
    mes_inicio_operaciones,
    tasa_descuento,
    df_amortizacion,
    frecuencia_meses
):

    # --------------------------------------------------
    # TASA DE DESCUENTO
    # --------------------------------------------------

    tasa_descuento_decimal = (
        tasa_descuento / 100
    )

    tasa_descuento_mensual = (
        (1 + tasa_descuento_decimal)
        ** (1 / 12)
        - 1
    )

    # --------------------------------------------------
    # FLUJO ECONÓMICO
    # --------------------------------------------------

    flujo_economico = [
        -monto_proyecto
    ]

    for mes in range(
        1,
        horizonte_meses + 1
    ):

        if mes < mes_inicio_operaciones:

            flujo_mes_economico = 0

        else:

            flujo_mes_economico = (
                flujo_operativo
            )

        flujo_economico.append(
            flujo_mes_economico
        )

    # --------------------------------------------------
    # FLUJO FINANCIERO
    # --------------------------------------------------

    flujo_financiero = [
        -aporte_propio
    ]

    pagos_por_mes = {}

    if not df_amortizacion.empty:

        for _, fila in (
            df_amortizacion.iterrows()
        ):

            mes_pago = (
                int(fila["Periodo"])
                * frecuencia_meses
            )

            pagos_por_mes[
                mes_pago
            ] = fila["Cuota"]

    for mes in range(
        1,
        horizonte_meses + 1
    ):

        pago_deuda = (
            pagos_por_mes.get(
                mes,
                0
            )
        )

        if mes < mes_inicio_operaciones:

            flujo_operativo_mes = 0

        else:

            flujo_operativo_mes = (
                flujo_operativo
            )

        flujo_mes_financiero = (
            flujo_operativo_mes
            - pago_deuda
        )

        flujo_financiero.append(
            flujo_mes_financiero
        )

    # --------------------------------------------------
    # VAN
    # --------------------------------------------------

    van_economico = npf.npv(
        tasa_descuento_mensual,
        flujo_economico
    )

    van_financiero = npf.npv(
        tasa_descuento_mensual,
        flujo_financiero
    )

    # --------------------------------------------------
    # TIR
    # --------------------------------------------------

    tir_economica_mensual = npf.irr(
        flujo_economico
    )

    tir_financiera_mensual = npf.irr(
        flujo_financiero
    )

    if pd.notna(
        tir_economica_mensual
    ):

        tir_economica_anual = (
            (1 + tir_economica_mensual)
            ** 12
            - 1
        )

    else:

        tir_economica_anual = None

    if pd.notna(
        tir_financiera_mensual
    ):

        tir_financiera_anual = (
            (1 + tir_financiera_mensual)
            ** 12
            - 1
        )

    else:

        tir_financiera_anual = None

    # --------------------------------------------------
    # FLUJOS ACUMULADOS
    # --------------------------------------------------

    acumulado_economico = 0
    acumulado_financiero = 0

    flujo_acumulado_economico = []
    flujo_acumulado_financiero = []

    for flujo in flujo_economico:

        acumulado_economico += flujo

        flujo_acumulado_economico.append(
            acumulado_economico
        )

    for flujo in flujo_financiero:

        acumulado_financiero += flujo

        flujo_acumulado_financiero.append(
            acumulado_financiero
        )

    # --------------------------------------------------
    # RECUPERACIÓN ECONÓMICA
    # --------------------------------------------------

    mes_recuperacion_economica = None

    for mes, acumulado in enumerate(
        flujo_acumulado_economico
    ):

        if acumulado >= 0:

            mes_recuperacion_economica = mes
            break

    # --------------------------------------------------
    # RECUPERACIÓN FINANCIERA
    # --------------------------------------------------

    mes_recuperacion_financiera = None

    if aporte_propio > 0:

        for mes, acumulado in enumerate(
            flujo_acumulado_financiero
        ):

            if acumulado >= 0:

                mes_recuperacion_financiera = mes
                break

    else:

        mes_recuperacion_financiera = (
            "No aplica"
        )

    # --------------------------------------------------
    # ETAPAS DEL PROYECTO
    # --------------------------------------------------

    estado_operacion = [
        "Inversión inicial"
    ]

    for mes in range(
        1,
        horizonte_meses + 1
    ):

        if mes < mes_inicio_operaciones:

            estado_operacion.append(
                "Preoperativo"
            )

        else:

            estado_operacion.append(
                "Operación"
            )

    # --------------------------------------------------
    # DATAFRAME DEL FLUJO
    # --------------------------------------------------

    df_flujo = pd.DataFrame(
        {
            "Mes": range(
                0,
                horizonte_meses + 1
            ),
            "Etapa": estado_operacion,
            "Flujo económico":
                flujo_economico,
            "Acumulado económico":
                flujo_acumulado_economico,
            "Flujo financiero":
                flujo_financiero,
            "Acumulado financiero":
                flujo_acumulado_financiero
        }
    )

    # --------------------------------------------------
    # DEVOLVER RESULTADOS
    # --------------------------------------------------

    return {
        "tasa_descuento_decimal":
            tasa_descuento_decimal,

        "tasa_descuento_mensual":
            tasa_descuento_mensual,

        "flujo_economico":
            flujo_economico,

        "flujo_financiero":
            flujo_financiero,

        "flujo_acumulado_economico":
            flujo_acumulado_economico,

        "flujo_acumulado_financiero":
            flujo_acumulado_financiero,

        "van_economico":
            van_economico,

        "van_financiero":
            van_financiero,

        "tir_economica_anual":
            tir_economica_anual,

        "tir_financiera_anual":
            tir_financiera_anual,

        "mes_recuperacion_economica":
            mes_recuperacion_economica,

        "mes_recuperacion_financiera":
            mes_recuperacion_financiera,

        "df_flujo":
            df_flujo
    }
