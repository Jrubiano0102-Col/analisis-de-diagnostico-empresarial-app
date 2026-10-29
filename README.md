# Diagnóstico Empresarial Multidimensional

Aplicación de escritorio en Python para el análisis, diagnóstico y visualización de indicadores empresariales clave (KPIs), tablas dinámicas, gráficas y detección causal de situaciones críticas a partir de archivos **Excel (.xlsx, .xls)** y **CSV**.

---

## 🚀 Funcionalidades de la Aplicación

### 1. Indicadores Empresariales Procesados
- **Ingresos por ventas**: Valor económico total generado por las transacciones.
- **Unidades vendidas**: Cantidad total de productos comercializados.
- **Ticket promedio**: Ingresos divididos entre el número de pedidos (`Ingresos / Pedidos`).
- **Margen bruto**: Relación porcentual entre los ingresos y los costos de los productos vendidos.
- **Variación de ventas**: Cambio porcentual entre periodos (desglose temporal completo y variación último periodo vs anterior).
- **Participación comercial**: Cuota porcentual que aporta cada región o segmento respecto al total de ventas.

### 2. Detección Automática de Situaciones que Requieren Atención
El motor analítico evalúa el dataset para identificar y diagnosticar 6 situaciones críticas:
1. 📉 **Disminución de ventas en determinados periodos**: Alerta caídas entre periodos y mide la cuantía de la contracción.
2. 📦 **Productos con bajo desempeño comercial**: Detecta artículos o líneas con ventas o márgenes significativamente inferiores al promedio.
3. 🗺️ **Regiones con resultados inferiores a otras**: Compara regiones e identifica territorios rezagados en ventas o rentabilidad.
4. 🌐 **Canales que presentan reducción de ingresos**: Monitorea la tendencia de ventas por canal (Online, Tienda Física, Mayorista/Distribuidor).
5. 🏷️ **Cambios de precios asociados con variaciones de ventas**: Detecta elasticidad y sensibilidad negativa (incrementos de precios que desploman el volumen).
6. 📊 **Productos con posibles dificultades de inventario**: Detecta riesgo inminente de quiebre de stock (*stockout*) y sobreinventario / capital inmovilizado.

### 3. Vistas y Módulos del Dashboard
- **📊 Indicadores Clave & KPIs**: 6 tarjetas directas con métricas consolidadas y dos tablas de desglose (variación periodo a periodo y participación comercial).
- **📈 Gráficas y Tendencias**: Tablero 2x2 interactivo con Matplotlib y selector de vistas individuales (Ventas vs Costos, Margen por Región, Participación %, Unidades & Ticket, Desempeño por Producto/Canal, Sensibilidad de Precios e Inventarios).
- **🚨 Situaciones de Atención**: Listado interactivo con filtros por categoría (Periodo, Producto, Región, Canal, Precio, Inventario), severidad (*Crítico, Alerta, Óptimo*), hallazgo numérico, causa raíz y plan de acción.
- **📋 Vista de Tabla**: Explorador de los datos originales con desplazamiento vertical y horizontal.
- **📥 Exportación de Informe**: Genera un archivo `.txt` o `.md` con el diagnóstico completo.

---

## 🛠️ Ejecución

Hacer doble clic en:
```
iniciar.bat
```
O desde la consola:
```powershell
python main.py
```
*(Carga el archivo [`ejemplo_diagnostico_empresarial.csv`](./ejemplo_diagnostico_empresarial.csv) para explorar todas las situaciones de atención en acción).*
