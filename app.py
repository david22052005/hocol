import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Dashboard de Pagos", layout="wide")

st.title("📊 Dashboard de Pagos a Contratistas")
st.markdown("---")

# Widget para subir archivo
uploaded_file = st.file_uploader(
    "📁 Sube tu archivo Excel",
    type=["xlsx", "xls"],
    help="Sube el archivo con los datos de facturación"
)

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file)
        
        # Limpieza de datos - Eliminar filas con TOTAL PAGADO vacío o cero
        df['TOTAL PAGADO'] = pd.to_numeric(
            df['TOTAL PAGADO'].astype(str).str.replace(r'[^\d.]', '', regex=True),
            errors='coerce'
        )
        df['CANTIDAD SUMINISTRADA'] = pd.to_numeric(
            df['CANTIDAD SUMINISTRADA'].astype(str).str.replace(r'[^\d.]', '', regex=True),
            errors='coerce'
        )
        df['PRECIO UNITARIO'] = pd.to_numeric(
            df['PRECIO UNITARIO'].astype(str).str.replace(r'[^\d.]', '', regex=True),
            errors='coerce'
        )
        
        df = df.dropna(subset=['TOTAL PAGADO'])
        df = df[df['TOTAL PAGADO'] > 0]
        
        st.success(f"✅ Archivo cargado exitosamente: **{len(df)} registros encontrados**")
        
        # Sidebar para filtros
        st.sidebar.header("🔍 Filtros")
        
        # 🔹 NUEVO: Filtro por CONTRATISTA (primero para priorizar)
        contratistas = sorted(df['CONTRATISTA'].dropna().unique())
        contratista_seleccionado = st.sidebar.multiselect(
            "Seleccionar Contratista(s):",
            options=contratistas,
            default=contratistas
        )
        
        # Filtro por AÑO
        anios = sorted(df['AÑO'].unique())
        año_seleccionado = st.sidebar.multiselect(
            "Seleccionar Año(s):",
            options=anios,
            default=anios
        )
        
        # Filtro por MES (ordenado cronológicamente)
        orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        meses_disponibles = [m for m in orden_meses if m in df['MES DE FACTURACION'].unique()]
        mes_seleccionado = st.sidebar.multiselect(
            "Seleccionar Mes(es):",
            options=meses_disponibles,
            default=meses_disponibles
        )
        
        # Filtro por CATEGORIA
        categorias = sorted(df['CATEGORIA'].unique())
        categoria_seleccionada = st.sidebar.multiselect(
            "Seleccionar Categoría(s):",
            options=categorias,
            default=categorias
        )
        
        # Filtro por CAMPO
        campos = sorted(df['CAMPO'].unique())
        campo_seleccionado = st.sidebar.multiselect(
            "Seleccionar Campo(s):",
            options=campos,
            default=campos
        )
        
        # Filtro por SERVICIO
        servicios = sorted(df['SERVICIO'].dropna().unique())
        servicio_seleccionado = st.sidebar.multiselect(
            "Seleccionar Servicio(s):",
            options=servicios,
            default=servicios
        )
        
        # Aplicar filtros (incluyendo CONTRATISTA)
        df_filtrado = df[
            (df['CONTRATISTA'].isin(contratista_seleccionado)) &
            (df['AÑO'].isin(año_seleccionado)) &
            (df['MES DE FACTURACION'].isin(mes_seleccionado)) &
            (df['CATEGORIA'].isin(categoria_seleccionada)) &
            (df['CAMPO'].isin(campo_seleccionado)) &
            (df['SERVICIO'].isin(servicio_seleccionado))
        ]
        
        if len(df_filtrado) == 0:
            st.warning("⚠️ No hay datos con los filtros seleccionados")
        else:
            # ========== MÉTRICAS PRINCIPALES ==========
            st.subheader("📈 Resumen General")
            
            # Calcular métricas
            total_pagado = df_filtrado['TOTAL PAGADO'].sum()
            total_cantidad = df_filtrado['CANTIDAD SUMINISTRADA'].sum()
            avg_precio = df_filtrado['PRECIO UNITARIO'].mean()
            num_contratistas = df_filtrado['CONTRATISTA'].nunique()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total Pagado", f"${total_pagado:,.0f}")
            col2.metric("📦 Cantidad Total", f"{total_cantidad:,.0f}")
            col3.metric("🏷️ Precio Unitario Prom.", f"${avg_precio:,.0f}")
            col4.metric("👥 Contratistas", num_contratistas)
            
            st.markdown("---")
            
            # ========== GRÁFICA 1: Pagos por Contratista ==========
            st.subheader("💰 Pagos por Contratista")
            pagos_por_contratista = df_filtrado.groupby('CONTRATISTA')['TOTAL PAGADO'].sum().reset_index()
            pagos_por_contratista = pagos_por_contratista.sort_values('TOTAL PAGADO', ascending=False)
            
            fig_barras = px.bar(
                pagos_por_contratista,
                x='TOTAL PAGADO',
                y='CONTRATISTA',
                orientation='h',
                title='Total Pagado por Contratista',
                color='TOTAL PAGADO',
                color_continuous_scale='Blues',
                text_auto='.2s'
            )
            fig_barras.update_layout(yaxis={'categoryorder': 'total ascending'}, height=350, showlegend=False)
            st.plotly_chart(fig_barras, use_container_width=True)
            
            # ========== GRÁFICA 2: CANTIDAD SUMINISTRADA por Contratista ==========
            st.subheader("📦 Cantidad Suministrada por Contratista")
            
            cantidad_por_contratista = df_filtrado.groupby('CONTRATISTA')['CANTIDAD SUMINISTRADA'].sum().reset_index()
            cantidad_por_contratista = cantidad_por_contratista.sort_values('CANTIDAD SUMINISTRADA', ascending=False)
            
            fig_cantidad = px.bar(
                cantidad_por_contratista,
                x='CANTIDAD SUMINISTRADA',
                y='CONTRATISTA',
                orientation='h',
                title='Total de Unidades Suministradas por Contratista',
                color='CANTIDAD SUMINISTRADA',
                color_continuous_scale='Greens',
                text_auto='.2s'
            )
            fig_cantidad.update_layout(yaxis={'categoryorder': 'total ascending'}, height=350, showlegend=False)
            st.plotly_chart(fig_cantidad, use_container_width=True)
            
            # ========== GRÁFICA 3: Relación Cantidad vs Precio Unitario ==========
            st.subheader("🔍 Relación: Cantidad vs Precio Unitario")
            
            relacion_df = df_filtrado.groupby('CONTRATISTA').agg({
                'CANTIDAD SUMINISTRADA': 'sum',
                'PRECIO UNITARIO': 'mean',
                'TOTAL PAGADO': 'sum'
            }).reset_index()
            
            fig_scatter = px.scatter(
                relacion_df,
                x='CANTIDAD SUMINISTRADA',
                y='PRECIO UNITARIO',
                size='TOTAL PAGADO',
                color='CONTRATISTA',
                title='Precio Unitario vs Cantidad Suministrada (tamaño = Total Pagado)',
                hover_data=['CONTRATISTA'],
                size_max=60
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # ========== GRÁFICA 4: Distribución Porcentual de Pagos ==========
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🥧 Distribución de Pagos")
                fig_torta = px.pie(
                    pagos_por_contratista,
                    values='TOTAL PAGADO',
                    names='CONTRATISTA',
                    title='Distribución Porcentual',
                    hole=0.3
                )
                fig_torta.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_torta, use_container_width=True)
            
            with col2:
                st.subheader("📊 Tabla Detallada")
                df_tabla = pagos_por_contratista.copy()
                df_tabla['TOTAL PAGADO'] = df_tabla['TOTAL PAGADO'].map('${:,.0f}'.format)
                df_tabla['% DEL TOTAL'] = (
                    pagos_por_contratista['TOTAL PAGADO'] / pagos_por_contratista['TOTAL PAGADO'].sum() * 100
                ).map('{:.2f}%'.format)
                st.dataframe(df_tabla, use_container_width=True)
            
            # ========== GRÁFICA 5: Evolución Mensual de Cantidad ==========
            if 'MES DE FACTURACION' in df_filtrado.columns and len(mes_seleccionado) > 0:
                st.markdown("---")
                st.subheader("📅 Evolución Mensual: Cantidad Suministrada")
                
                evolucion_cantidad = df_filtrado.groupby(
                    ['MES DE FACTURACION', 'CONTRATISTA']
                )['CANTIDAD SUMINISTRADA'].sum().reset_index()
                
                evolucion_cantidad['MES DE FACTURACION'] = pd.Categorical(
                    evolucion_cantidad['MES DE FACTURACION'],
                    categories=orden_meses,
                    ordered=True
                )
                evolucion_cantidad = evolucion_cantidad.sort_values('MES DE FACTURACION')
                
                fig_evolucion = px.line(
                    evolucion_cantidad,
                    x='MES DE FACTURACION',
                    y='CANTIDAD SUMINISTRADA',
                    color='CONTRATISTA',
                    title='Cantidad Suministrada por Mes',
                    markers=True
                )
                fig_evolucion.update_layout(height=400, xaxis_title="Mes", yaxis_title="Cantidad")
                st.plotly_chart(fig_evolucion, use_container_width=True)
            
            # ========== GRÁFICA 6: Distribución por Mes (Pagos) ==========
            if len(mes_seleccionado) > 0:
                st.markdown("---")
                st.subheader("🗓️ Pagos por Mes y Contratista")
                
                por_mes = df_filtrado.groupby(['MES DE FACTURACION', 'CONTRATISTA'])['TOTAL PAGADO'].sum().reset_index()
                por_mes['MES DE FACTURACION'] = pd.Categorical(
                    por_mes['MES DE FACTURACION'],
                    categories=orden_meses,
                    ordered=True
                )
                por_mes = por_mes.sort_values('MES DE FACTURACION')
                
                fig_mes = px.bar(
                    por_mes,
                    x='MES DE FACTURACION',
                    y='TOTAL PAGADO',
                    color='CONTRATISTA',
                    title='Evolución de Pagos por Mes',
                    barmode='group',
                    text_auto='.2s'
                )
                fig_mes.update_layout(height=400)
                st.plotly_chart(fig_mes, use_container_width=True)
            
            # ========== GRÁFICA 7: Distribución por Servicio ==========
            if len(servicio_seleccionado) > 0:
                st.markdown("---")
                st.subheader("🔧 Pagos por Servicio y Contratista")
                
                por_servicio = df_filtrado.groupby(['SERVICIO', 'CONTRATISTA'])['TOTAL PAGADO'].sum().reset_index()
                
                fig_servicio = px.bar(
                    por_servicio,
                    x='SERVICIO',
                    y='TOTAL PAGADO',
                    color='CONTRATISTA',
                    title='Distribución por Servicio',
                    barmode='group',
                    text_auto='.2s'
                )
                fig_servicio.update_layout(height=400)
                st.plotly_chart(fig_servicio, use_container_width=True)
            
            # ========== 🔹 NUEVA SECCIÓN: COMPARACIÓN AÑO VS AÑO ==========
            st.markdown("---")
            st.subheader("📊 Comparación Año vs Año")
            
            # Verificar si hay más de un año en los datos filtrados
            anios_unicos = sorted(df_filtrado['AÑO'].unique())
            
            if len(anios_unicos) >= 2:
                # Selectores para elegir los dos años a comparar
                col_sel1, col_sel2 = st.columns(2)
                
                with col_sel1:
                    año_base = st.selectbox(
                        "📅 Año Base (comparación):",
                        options=anios_unicos,
                        index=0  # Siempre seguro: primer año de la lista
                    )
                
                with col_sel2:
                    # Crear lista de años disponibles excluyendo el base
                    opciones_comparacion = [a for a in anios_unicos if a != año_base]
                    
                    # 🔹 CORRECCIÓN: Validar que haya opciones y calcular índice seguro
                    if len(opciones_comparacion) > 0:
                        idx_default = min(1, len(opciones_comparacion) - 1)  # Índice seguro
                        año_comparacion = st.selectbox(
                            "📅 Año de Comparación:",
                            options=opciones_comparacion,
                            index=idx_default
                        )
                    else:
                        st.warning("⚠️ No hay años disponibles para comparar")
                        año_comparacion = None
                
                # Solo continuar si ambos años están seleccionados
                if año_comparacion is not None:
                    # Filtrar datos por cada año
                    df_año_base = df_filtrado[df_filtrado['AÑO'] == año_base]
                    df_año_comp = df_filtrado[df_filtrado['AÑO'] == año_comparacion]
                    
                    # Calcular métricas para cada año
                    total_base = df_año_base['TOTAL PAGADO'].sum()
                    total_comp = df_año_comp['TOTAL PAGADO'].sum()
                    cantidad_base = df_año_base['CANTIDAD SUMINISTRADA'].sum()
                    cantidad_comp = df_año_comp['CANTIDAD SUMINISTRADA'].sum()
                    precio_base = df_año_base['PRECIO UNITARIO'].mean()
                    precio_comp = df_año_comp['PRECIO UNITARIO'].mean()
                    
                    # Calcular variaciones (evitar división por cero)
                    var_pago = total_comp - total_base
                    var_pago_pct = ((total_comp - total_base) / total_base * 100) if total_base != 0 else 0
                    var_cantidad = cantidad_comp - cantidad_base
                    var_cantidad_pct = ((cantidad_comp - cantidad_base) / cantidad_base * 100) if cantidad_base != 0 else 0
                    var_precio = precio_comp - precio_base
                    var_precio_pct = ((precio_comp - precio_base) / precio_base * 100) if precio_base != 0 else 0
                    
                    # Mostrar métricas comparativas
                    st.markdown(f"### 📈 {año_base} vs {año_comparacion}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            label="💰 Total Pagado",
                            value=f"${total_comp:,.0f}",
                            delta=f"{var_pago:,.0f} ({var_pago_pct:+.1f}%)",
                            delta_color="inverse" if var_pago < 0 else "normal"
                        )
                        st.caption(f"Año {año_base}: ${total_base:,.0f}")
                    
                    with col2:
                        st.metric(
                            label="📦 Cantidad Suministrada",
                            value=f"{cantidad_comp:,.0f}",
                            delta=f"{var_cantidad:,.0f} ({var_cantidad_pct:+.1f}%)",
                            delta_color="inverse" if var_cantidad < 0 else "normal"
                        )
                        st.caption(f"Año {año_base}: {cantidad_base:,.0f}")
                    
                    with col3:
                        st.metric(
                            label="🏷️ Precio Unitario Prom.",
                            value=f"${precio_comp:,.0f}",
                            delta=f"{var_precio:,.0f} ({var_precio_pct:+.1f}%)",
                            delta_color="inverse" if var_precio < 0 else "normal"
                        )
                        st.caption(f"Año {año_base}: ${precio_base:,.0f}")
                    
                    st.markdown("---")
                    
                    # Gráfica comparativa: Pagos por mes entre los dos años
                    if 'MES DE FACTURACION' in df.columns:
                        st.subheader(f"📅 Comparación Mensual: {año_base} vs {año_comparacion}")
                        
                        # Agrupar por mes para cada año
                        pagos_mes_base = df_año_base.groupby('MES DE FACTURACION')['TOTAL PAGADO'].sum().reset_index()
                        pagos_mes_comp = df_año_comp.groupby('MES DE FACTURACION')['TOTAL PAGADO'].sum().reset_index()
                        
                        # Ordenar meses correctamente
                        pagos_mes_base['MES DE FACTURACION'] = pd.Categorical(
                            pagos_mes_base['MES DE FACTURACION'], categories=orden_meses, ordered=True
                        )
                        pagos_mes_comp['MES DE FACTURACION'] = pd.Categorical(
                            pagos_mes_comp['MES DE FACTURACION'], categories=orden_meses, ordered=True
                        )
                        pagos_mes_base = pagos_mes_base.sort_values('MES DE FACTURACION')
                        pagos_mes_comp = pagos_mes_comp.sort_values('MES DE FACTURACION')
                        
                        # Combinar dataframes
                        comparacion_mensual = pd.merge(
                            pagos_mes_base, 
                            pagos_mes_comp, 
                            on='MES DE FACTURACION', 
                            suffixes=(f'_{año_base}', f'_{año_comparacion}'),
                            how='outer'
                        ).fillna(0)
                        
                        # Crear gráfica de líneas comparativa
                        fig_comp_linea = go.Figure()
                        
                        fig_comp_linea.add_trace(go.Scatter(
                            x=comparacion_mensual['MES DE FACTURACION'],
                            y=comparacion_mensual[f'TOTAL PAGADO_{año_base}'],
                            mode='lines+markers',
                            name=f'{año_base}',
                            line=dict(color='blue', width=3),
                            marker=dict(size=8)
                        ))
                        
                        fig_comp_linea.add_trace(go.Scatter(
                            x=comparacion_mensual['MES DE FACTURACION'],
                            y=comparacion_mensual[f'TOTAL PAGADO_{año_comparacion}'],
                            mode='lines+markers',
                            name=f'{año_comparacion}',
                            line=dict(color='red', width=3),
                            marker=dict(size=8)
                        ))
                        
                        fig_comp_linea.update_layout(
                            title=f'Evolución Mensual Comparada: {año_base} vs {año_comparacion}',
                            xaxis_title='Mes',
                            yaxis_title='Total Pagado (COP)',
                            hovermode='x unified',
                            height=400,
                            legend=dict(x=0, y=1)
                        )
                        st.plotly_chart(fig_comp_linea, use_container_width=True)
                        
                        # Gráfica de barras comparativa por mes
                        fig_comp_barras = go.Figure()
                        
                        fig_comp_barras.add_trace(go.Bar(
                            x=comparacion_mensual['MES DE FACTURACION'],
                            y=comparacion_mensual[f'TOTAL PAGADO_{año_base}'],
                            name=f'{año_base}',
                            marker_color='blue'
                        ))
                        
                        fig_comp_barras.add_trace(go.Bar(
                            x=comparacion_mensual['MES DE FACTURACION'],
                            y=comparacion_mensual[f'TOTAL PAGADO_{año_comparacion}'],
                            name=f'{año_comparacion}',
                            marker_color='red'
                        ))
                        
                        fig_comp_barras.update_layout(
                            title=f'Comparación de Pagos por Mes: {año_base} vs {año_comparacion}',
                            xaxis_title='Mes',
                            yaxis_title='Total Pagado (COP)',
                            barmode='group',
                            height=400
                        )
                        st.plotly_chart(fig_comp_barras, use_container_width=True)
                    
                    # Comparación por contratista entre años
                    st.subheader(f"👥 Comparación por Contratista: {año_base} vs {año_comparacion}")
                    
                    pagos_contratista_base = df_año_base.groupby('CONTRATISTA')['TOTAL PAGADO'].sum().reset_index()
                    pagos_contratista_comp = df_año_comp.groupby('CONTRATISTA')['TOTAL PAGADO'].sum().reset_index()
                    
                    # Combinar
                    comparacion_contratista = pd.merge(
                        pagos_contratista_base,
                        pagos_contratista_comp,
                        on='CONTRATISTA',
                        suffixes=(f'_{año_base}', f'_{año_comparacion}'),
                        how='outer'
                    ).fillna(0)
                    
                    # Calcular variación
                    comparacion_contratista['Variacion'] = (
                        comparacion_contratista[f'TOTAL PAGADO_{año_comparacion}'] - 
                        comparacion_contratista[f'TOTAL PAGADO_{año_base}']
                    )
                    comparacion_contratista['Variacion_Pct'] = (
                        comparacion_contratista['Variacion'] / 
                        comparacion_contratista[f'TOTAL PAGADO_{año_base}'].replace(0, pd.NA) * 100
                    ).fillna(0)
                    
                    # Ordenar por variación
                    comparacion_contratista = comparacion_contratista.sort_values('Variacion', ascending=False)
                    
                    # Gráfica de variación
                    fig_var = px.bar(
                        comparacion_contratista,
                        x='CONTRATISTA',
                        y='Variacion',
                        color='Variacion',
                        color_continuous_scale='RdYlGn',
                        title=f'Variación de Pagos por Contratista: {año_comparacion} vs {año_base}',
                        text_auto='.2s'
                    )
                    fig_var.update_layout(
                        height=400,
                        xaxis_title='Contratista',
                        yaxis_title=f'Variación (COP)',
                        showlegend=False
                    )
                    st.plotly_chart(fig_var, use_container_width=True)
                    
                    # Tabla detallada de comparación
                    st.subheader("📋 Tabla Detallada de Comparación")
                    df_comp_tabla = comparacion_contratista.copy()
                    df_comp_tabla[f'TOTAL PAGADO_{año_base}'] = df_comp_tabla[f'TOTAL PAGADO_{año_base}'].map('${:,.0f}'.format)
                    df_comp_tabla[f'TOTAL PAGADO_{año_comparacion}'] = df_comp_tabla[f'TOTAL PAGADO_{año_comparacion}'].map('${:,.0f}'.format)
                    df_comp_tabla['Variacion'] = df_comp_tabla['Variacion'].map('${:,.0f}'.format)
                    df_comp_tabla['Variacion_Pct'] = df_comp_tabla['Variacion_Pct'].map('{:+.2f}%'.format)
                    st.dataframe(df_comp_tabla, use_container_width=True)
                
            else:
                st.info("📊 Selecciona al menos 2 años diferentes en los filtros para activar la comparación Año vs Año")  
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
        st.error("Asegúrate de que el archivo tenga las columnas correctas")
else:
    st.info("👆 Por favor, sube un archivo Excel para comenzar")
    
    with st.expander("📋 Ver estructura esperada del archivo"):
        st.write("""
        **Columnas requeridas:**
        - MES DE FACTURACION
        - AÑO
        - CAMPO
        - CATEGORIA
        - SERVICIO
        - CONTRATISTA
        - ADMINISTRADOR
        - CANTIDAD SUMINISTRADA
        - PRECIO UNITARIO
        - TOTAL PAGADO
        """)