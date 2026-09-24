import streamlit as st

from modules.amortizacion import generar_amortizacion
from modules.evaluacion import evaluar_proyecto
from modules.reporte_excel import generar_reporte_excel
from modules.ingresos import generar_ingresos
from modules.costos import generar_costos

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

st.markdown("### Ingresos")

numero_productos = st.number_input(
    "Número de productos o servicios",
    min_value=1,
    max_value=10,
    value=1,
    step=1
)

productos = []

for i in range(
    int(numero_productos)
):

    st.markdown(
        f"#### Producto / Servicio {i + 1}"
    )

    col_ing1, col_ing2 = st.columns(2)

    nombre = col_ing1.text_input(
        "Nombre",
        value=f"Producto {i + 1}",
        key=f"nombre_producto_{i}"
    )

    precio_unitario = (
        col_ing2.number_input(
            "Precio unitario",
            min_value=0.0,
            value=100.0,
            step=1.0,
            key=f"precio_producto_{i}"
        )
    )

    col_ing3, col_ing4 = st.columns(2)

    unidades_mensuales = (
        col_ing3.number_input(
            "Unidades mensuales",
            min_value=0.0,
            value=90.0,
            step=1.0,
            key=f"unidades_producto_{i}"
        )
    )

    mes_inicio_producto = (
        col_ing4.number_input(
            "Mes de inicio de ventas",
            min_value=int(
                mes_inicio_operaciones
            ),
            value=int(
                mes_inicio_operaciones
            ),
            step=1,
            key=f"inicio_producto_{i}"
        )
    )

    crecimiento_anual = (
        st.number_input(
            "Crecimiento anual esperado (%)",
            min_value=-100.0,
            value=0.0,
            step=1.0,
            key=f"crecimiento_producto_{i}"
        )
    )

    productos.append(
        {
            "nombre": nombre,
            "precio_unitario":
                precio_unitario,
            "unidades_mensuales":
                unidades_mensuales,
            "mes_inicio":
                mes_inicio_producto,
            "crecimiento_anual":
                crecimiento_anual
        }
    )

st.markdown("### Costos")

# --------------------------------------------------
# COSTOS FIJOS
# --------------------------------------------------

st.markdown("#### Costos fijos")

numero_costos_fijos = st.number_input(
    "Número de costos fijos",
    min_value=1,
    max_value=10,
    value=1,
    step=1
)

costos_fijos_detalle = []

for i in range(
    int(numero_costos_fijos)
):

    col_cf1, col_cf2 = st.columns(2)

    nombre_costo = col_cf1.text_input(
        "Concepto",
        value=(
            "Arriendo"
            if i == 0
            else f"Costo fijo {i + 1}"
        ),
        key=f"nombre_costo_fijo_{i}"
    )

    monto_costo = col_cf2.number_input(
        "Monto mensual",
        min_value=0.0,
        value=2000.0 if i == 0 else 0.0,
        step=100.0,
        key=f"monto_costo_fijo_{i}"
    )

    costos_fijos_detalle.append(
        {
            "nombre": nombre_costo,
            "monto": monto_costo
        }
    )

# --------------------------------------------------
# NÓMINA
# --------------------------------------------------

st.markdown("#### Nómina")

nomina_mensual = st.number_input(
    "Costo mensual total de nómina",
    min_value=0.0,
    value=0.0,
    step=100.0,
    help=(
        "Por ahora se ingresa como un valor mensual total. "
        "Más adelante podrá detallarse por empleados, "
        "sueldos y beneficios."
    )
)

# --------------------------------------------------
# COSTOS VARIABLES
# --------------------------------------------------

st.markdown("#### Costos variables por producto")

costos_variables_unitarios = []

for i, producto in enumerate(
    productos
):

    costo_variable_unitario = (
        st.number_input(
            (
                "Costo variable unitario - "
                f"{producto['nombre']}"
            ),
            min_value=0.0,
            value=0.0,
            step=0.10,
            key=f"costo_variable_{i}"
        )
    )

    costos_variables_unitarios.append(
        costo_variable_unitario
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

    aporte_propio = (
        monto_proyecto
        - monto_financiado
    )

    # Ingreso mensual base.
    # Se conserva para resumen y reporte.
    ingresos = sum(
        producto["precio_unitario"]
        * producto["unidades_mensuales"]
        for producto in productos
    )

    # Costos mensuales base.
    # Se conservan para resumen y reporte.
    costos_fijos = (
        sum(
            costo["monto"]
            for costo in costos_fijos_detalle
        )
        + nomina_mensual
    )

    costos_variables = sum(
        producto["unidades_mensuales"]
        * costos_variables_unitarios[i]
        for i, producto in enumerate(
            productos
        )
    )

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

    # --------------------------------------------------
    # PROYECCIÓN DE INGRESOS
    # --------------------------------------------------

    ingresos_mensuales, df_ingresos = (
        generar_ingresos(
            productos=productos,
            horizonte_meses=horizonte_meses
        )
    )

    # --------------------------------------------------
    # PROYECCIÓN DE COSTOS
    # --------------------------------------------------

    (
        costos_mensuales,
        costos_fijos_mensuales,
        costos_variables_mensuales,
        nomina_mensual_proyectada,
        df_costos
    ) = generar_costos(
        productos=productos,
        costos_fijos_detalle=costos_fijos_detalle,
        nomina_mensual=nomina_mensual,
        costos_variables_unitarios=
            costos_variables_unitarios,
        horizonte_meses=horizonte_meses,
        mes_inicio_operaciones=
            mes_inicio_operaciones
    )

    # --------------------------------------------------
    # FLUJO OPERATIVO MENSUAL
    # --------------------------------------------------

    flujo_operativo_mensual = [
        0.0
        for _ in range(
            horizonte_meses + 1
        )
    ]

    for mes in range(
        1,
        horizonte_meses + 1
    ):

        flujo_operativo_mensual[
            mes
        ] = (
            ingresos_mensuales[mes]
            - costos_mensuales[mes]
        )

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
        flujo_operativo_mensual=flujo_operativo_mensual,
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
    # DATOS PARA EL REPORTE EXCEL
    # --------------------------------------------------

    datos_reporte = {
        "monto_proyecto": monto_proyecto,
        "monto_financiado": monto_financiado,
        "aporte_propio": aporte_propio,
        "tasa_interes": tasa_interes,
        "plazo_credito_meses": plazo_credito_meses,
        "frecuencia_pago": frecuencia_pago,
        "tipo_amortizacion": tipo_amortizacion,
        "tipo_gracia": tipo_gracia,
        "meses_gracia_calculo": meses_gracia_calculo,
        "mes_inicio_operaciones": mes_inicio_operaciones,
        "horizonte_meses": horizonte_meses,
        "ingresos": ingresos,
        "costos_fijos": costos_fijos,
        "costos_variables": costos_variables,
        "flujo_operativo": flujo_operativo,
        "tasa_descuento": tasa_descuento,
        "intereses_capitalizados": intereses_capitalizados,
        "saldo_despues_gracia": saldo_despues_gracia
    }

    excel_buffer = generar_reporte_excel(
        datos=datos_reporte,
        resultados=resultados,
        df_amortizacion=df_amortizacion,
        df_flujo=df_flujo
    )

    
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
