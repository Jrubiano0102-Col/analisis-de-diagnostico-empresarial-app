"""
analyzer.py
Motor de diagnóstico empresarial multidimensional con soporte universal para archivos Excel y CSV.
"""
import os
import tempfile
import re
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "dairo_matplotlib")

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class BusinessAnalyzer:
    """Motor analítico de diagnóstico multidimensional empresarial."""

    def __init__(self, data: Any, metadata: Dict[str, Any]):
        self.metadata = metadata
        if isinstance(data, pd.DataFrame):
            self.df = data.copy()
        elif isinstance(data, list) and metadata.get("columns"):
            self.df = pd.DataFrame(data, columns=metadata["columns"])
        else:
            self.df = pd.DataFrame()

        self._clean_and_prepare_df()
        self.col_map = self._map_columns()
        self.kpis: Dict[str, Any] = {}
        self.problems: List[Dict[str, Any]] = []
        self.dimensions_summary: Dict[str, Any] = {}
        self.detected_situations: Dict[str, Any] = {}

    def _clean_and_prepare_df(self):
        """Convierte y normaliza columnas numéricas y de fecha de archivos Excel y CSV."""
        for col in self.df.columns:
            # Si es columna datetime de Excel, formatear a string legible
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.df[col] = self.df[col].dt.strftime("%Y-%m")
                continue

            # Si ya es numérica nativa, no tocar
            if pd.api.types.is_numeric_dtype(self.df[col]):
                continue

            # Limpiar columnas que puedan contener números formateados como texto
            s = self.df[col].astype(str).str.strip()
            if s.empty:
                continue

            cleaned = (
                s.str.replace("$", "", regex=False)
                .str.replace("€", "", regex=False)
                .str.replace("S/.", "", regex=False)
                .str.replace("%", "", regex=False)
                .str.replace(" ", "", regex=False)
            )

            # Manejar números negativos entre paréntesis: (123.45) -> -123.45
            cleaned = cleaned.str.replace(r"^\((.*)\)$", r"-\1", regex=True)

            # Detectar si usa coma como decimal (ej. 1.234,56 o 1234,56)
            has_comma_dec = (cleaned.str.contains(r",\d{1,2}$", regex=True).sum()) > (len(cleaned) * 0.3)
            if has_comma_dec:
                cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            else:
                cleaned = cleaned.str.replace(",", "", regex=False)

            converted = pd.to_numeric(cleaned, errors="coerce")
            # Si al menos el 40% de los registros son números válidos y no vacíos
            if converted.notnull().sum() >= max(1, len(self.df) * 0.4):
                self.df[col] = converted

    def _map_columns(self) -> Dict[str, Optional[str]]:
        """Mapea heurísticamente las columnas con un diccionario exhaustivo de sinónimos."""
        mapping = {
            "period": None,
            "region": None,
            "canal": None,
            "producto": None,
            "dimension": None,
            "ventas": None,
            "costos": None,
            "margen": None,
            "pedidos": None,
            "unidades": None,
            "precio": None,
            "stock": None,
            "clientes": None,
            "nps": None,
            "devoluciones": None,
            "rotacion": None,
        }

        # Normalizar nombres de columnas a minúsculas sin acentos
        def _clean_str(s):
            s = str(s).lower().strip()
            replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"), ("_", " "), ("-", " "))
            for a, b in replacements:
                s = s.replace(a, b)
            return re.sub(r"\s+", " ", s)

        col_norm = {col: _clean_str(col) for col in self.df.columns}

        keywords = {
            "period": ["periodo", "fecha", "mes", "year", "ano", "trimestre", "quarter", "date", "dia", "semana", "tiempo"],
            "region": ["region", "sucursal", "zona", "ciudad", "pais", "sede", "area", "territorio", "tienda", "ubicacion", "departamento"],
            "canal": ["canal", "channel", "medio", "tipo canal", "via venta", "distribucion", "tipo venta", "canal venta"],
            "producto": ["producto", "product", "item", "articulo", "linea", "sku", "categoria", "rubro", "nombre producto", "familia", "descripcion", "detalle"],
            "dimension": ["dimension", "clasificacion", "segmento", "tipo"],
            "ventas": ["ventas usd", "ventas", "ingresos", "revenue", "sales", "facturacion", "total ventas", "monto", "importe", "total", "subtotal", "valor total", "valor venta", "precio total", "neto"],
            "costos": ["costos operativos", "costos", "costes", "gastos", "expenses", "cost", "cogs", "costo total", "costo venta", "costo producto", "gastos operativos"],
            "margen": ["margen bruto pct", "margen bruto", "margen", "utilidad pct", "profit margin", "margen pct", "rentabilidad", "utilidad", "% margen", "margen %"],
            "pedidos": ["pedidos", "ordenes", "transacciones", "orders", "tickets", "num pedidos", "nro pedido", "facturas", "id pedido", "codigo pedido", "num orden"],
            "unidades": ["unidades vendidas", "unidades", "cantidad", "quantity", "volumen", "qty", "cant", "piezas", "bultos", "items vendidos"],
            "precio": ["precio unitario", "precio", "price", "unit price", "pvp", "precio venta", "valor unitario"],
            "stock": ["stock inventario", "stock", "inventario", "inventory", "existencias", "unidades stock", "disponible", "saldo"],
            "clientes": ["nuevos clientes", "clientes", "customers", "leads", "usuarios", "compradores"],
            "nps": ["satisfaccion nps", "satisfaccion", "nps", "csat", "calificacion", "puntaje"],
            "devoluciones": ["devoluciones pct", "devoluciones", "defectos", "returns", "reclamaciones", "mermas", "rechazos"],
            "rotacion": ["rotacion personal pct", "rotacion", "turnover", "bajas personal", "ausentismo", "rotacion personal"]
        }

        # Búsqueda exacta primero, luego de contención
        for target, keys in keywords.items():
            # 1. Coincidencia exacta
            for orig_col, norm_col in col_norm.items():
                if norm_col in keys:
                    mapping[target] = orig_col
                    break
            # 2. Coincidencia por subcadena
            if not mapping[target]:
                for orig_col, norm_col in col_norm.items():
                    if any(k in norm_col for k in keys):
                        mapping[target] = orig_col
                        break

        # FALLBACK INTELIGENTE: Si no se detectó 'ventas', buscar la columna numérica con mayor suma positiva
        if not mapping["ventas"]:
            numeric_cols = [c for c in self.df.columns if pd.api.types.is_numeric_dtype(self.df[c])]
            best_col = None
            best_sum = -1
            for nc in numeric_cols:
                # Evitar columnas tipo ID o año (ej. 2024)
                if "id" in str(nc).lower() or str(nc).lower() in ["año", "year", "item"]:
                    continue
                s = self.df[nc].sum()
                if s > best_sum and s > 10:
                    best_sum = s
                    best_col = nc
            if best_col:
                mapping["ventas"] = best_col

        return mapping

    def set_custom_mapping(self, new_mapping: Dict[str, Optional[str]]):
        """Permite actualizar el mapeo de columnas manualmente desde la interfaz."""
        self.col_map.update(new_mapping)

    def run_full_diagnosis(self) -> Dict[str, Any]:
        """Ejecuta el análisis cuantitativo completo y la detección de situaciones que requieren atención."""
        self._calculate_core_indicators()
        self._detect_business_situations()
        self._summarize_dimensions()

        return {
            "kpis": self.kpis,
            "problems": self.problems,
            "detected_situations": self.detected_situations,
            "dimensions_summary": self.dimensions_summary,
            "column_mapping": self.col_map,
            "total_rows": len(self.df)
        }

    def _calculate_core_indicators(self):
        """Calcula los 6 indicadores empresariales base."""
        df = self.df
        cm = self.col_map
        k = {}

        # 1. Ingresos por ventas
        ventas_col = cm["ventas"]
        total_ventas = float(df[ventas_col].sum()) if ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]) else 0.0

        # 2. Costos de productos / operativos
        costos_col = cm["costos"]
        total_costos = float(df[costos_col].sum()) if costos_col and pd.api.types.is_numeric_dtype(df[costos_col]) else 0.0

        # 3. Unidades vendidas
        unidades_col = cm["unidades"]
        total_unidades = int(df[unidades_col].sum()) if unidades_col and pd.api.types.is_numeric_dtype(df[unidades_col]) else 0

        # 4. Ticket promedio
        pedidos_col = cm["pedidos"]
        total_pedidos = int(df[pedidos_col].sum()) if pedidos_col and pd.api.types.is_numeric_dtype(df[pedidos_col]) else 0
        if total_pedidos > 0 and total_ventas > 0:
            ticket_promedio = total_ventas / total_pedidos
        elif cm["clientes"] and pd.api.types.is_numeric_dtype(df[cm["clientes"]]) and df[cm["clientes"]].sum() > 0:
            ticket_promedio = total_ventas / float(df[cm["clientes"]].sum())
        else:
            ticket_promedio = 0.0

        # 5. Margen bruto
        margen_col = cm["margen"]
        if total_ventas > 0 and total_costos > 0:
            margen_bruto_pct = ((total_ventas - total_costos) / total_ventas) * 100.0
        elif margen_col and pd.api.types.is_numeric_dtype(df[margen_col]):
            margen_bruto_pct = float(df[margen_col].mean())
        else:
            margen_bruto_pct = 0.0

        min_margen = float(df[margen_col].min()) if (margen_col and pd.api.types.is_numeric_dtype(df[margen_col])) else margen_bruto_pct

        # 6. Variación de ventas periodo a periodo
        period_col = cm["period"]
        variacion_periodos = []
        variacion_ultimo_pct = 0.0
        crecimiento_global_pct = 0.0

        if period_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]):
            ventas_por_periodo = df.groupby(period_col, sort=False)[ventas_col].sum()
            periodos_list = list(ventas_por_periodo.index)
            valores_list = list(ventas_por_periodo.values)

            for i in range(len(periodos_list)):
                p_curr = periodos_list[i]
                v_curr = float(valores_list[i])
                if i == 0:
                    var_pct = 0.0
                else:
                    v_prev = float(valores_list[i - 1])
                    var_pct = ((v_curr - v_prev) / v_prev) * 100.0 if v_prev > 0 else 0.0

                variacion_periodos.append({
                    "periodo": str(p_curr),
                    "ventas": v_curr,
                    "variacion_pct": var_pct
                })

            if len(valores_list) >= 2:
                variacion_ultimo_pct = variacion_periodos[-1]["variacion_pct"]
                primero = valores_list[0]
                ultimo = valores_list[-1]
                crecimiento_global_pct = ((ultimo - primero) / primero) * 100.0 if primero > 0 else 0.0

        # 7. Participación comercial por región / segmento
        region_col = cm["region"] or cm["dimension"]
        participacion_comercial = []
        if region_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]) and total_ventas > 0:
            ventas_por_region = df.groupby(region_col)[ventas_col].sum().sort_values(ascending=False)
            for reg, v_reg in ventas_por_region.items():
                pct = (float(v_reg) / total_ventas) * 100.0
                participacion_comercial.append({
                    "segmento": str(reg),
                    "ventas": float(v_reg),
                    "participacion_pct": pct
                })

        # Indicadores complementarios
        dev_col = cm["devoluciones"]
        avg_dev = float(df[dev_col].mean()) if dev_col and pd.api.types.is_numeric_dtype(df[dev_col]) else 0.0
        max_dev = float(df[dev_col].max()) if dev_col and pd.api.types.is_numeric_dtype(df[dev_col]) else 0.0

        rot_col = cm["rotacion"]
        avg_rot = float(df[rot_col].mean()) if rot_col and pd.api.types.is_numeric_dtype(df[rot_col]) else 0.0
        max_rot = float(df[rot_col].max()) if rot_col and pd.api.types.is_numeric_dtype(df[rot_col]) else 0.0

        k["ingresos_ventas"] = total_ventas
        k["costos_operativos"] = total_costos
        k["utilidad_bruta"] = total_ventas - total_costos
        k["unidades_vendidas"] = total_unidades
        k["total_pedidos"] = total_pedidos
        k["ticket_promedio"] = ticket_promedio
        k["margen_bruto_pct"] = margen_bruto_pct
        k["margen_minimo_pct"] = min_margen
        k["variacion_ventas_ultimo_pct"] = variacion_ultimo_pct
        k["crecimiento_global_pct"] = crecimiento_global_pct
        k["variacion_periodos"] = variacion_periodos
        k["participacion_comercial"] = participacion_comercial
        k["estado_margen"] = "Óptimo" if margen_bruto_pct >= 35 else ("Alerta" if margen_bruto_pct >= 20 else "Crítico")
        k["calidad"] = {"devoluciones_promedio": avg_dev, "devoluciones_maxima": max_dev}
        k["talento"] = {"rotacion_promedio": avg_rot, "rotacion_maxima": max_rot}

        self.kpis = k

    def _detect_business_situations(self):
        """Detecta las 6 situaciones específicas que requieren atención."""
        problems = []
        situations: Dict[str, Any] = {}
        df = self.df
        cm = self.col_map

        period_col = cm["period"]
        ventas_col = cm["ventas"]
        region_col = cm["region"]
        canal_col = cm["canal"]
        producto_col = cm["producto"]
        precio_col = cm["precio"]
        stock_col = cm["stock"]
        unidades_col = cm["unidades"]
        margen_col = cm["margen"]

        # 1. Disminución de ventas en periodos
        situations["disminucion_ventas"] = []
        if period_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]):
            ventas_p = df.groupby(period_col, sort=False)[ventas_col].sum()
            p_keys = list(ventas_p.index)
            for i in range(1, len(p_keys)):
                p_prev, p_curr = p_keys[i-1], p_keys[i]
                v_prev, v_curr = float(ventas_p[p_prev]), float(ventas_p[p_curr])
                if v_curr < v_prev:
                    drop_val = v_prev - v_curr
                    drop_pct = (drop_val / v_prev) * 100.0
                    situations["disminucion_ventas"].append({
                        "periodo": str(p_curr), "periodo_anterior": str(p_prev),
                        "ventas_actuales": v_curr, "ventas_anteriores": v_prev,
                        "caida_monto": drop_val, "caida_pct": drop_pct
                    })
                    problems.append({
                        "id": f"SIT-01-PER-{p_curr}",
                        "dimension": "Comercial / Temporal",
                        "tipo": "Disminución de ventas en periodo",
                        "nivel": "CRÍTICO" if drop_pct >= 10.0 else "ALERTA",
                        "titulo": f"Disminución de Ventas en {p_curr}",
                        "hallazgo": f"En el periodo '{p_curr}' las ventas cayeron un {drop_pct:.2f}% (-${drop_val:,.0f} USD) respecto a '{p_prev}'.",
                        "causa_probable": "Efecto estacional, saturación temporal de demanda o reducción en la prospección comercial.",
                        "accion": "Analizar la evolución de pedidos en dicho periodo e implementar promociones de impulso en los meses de menor actividad."
                    })

        # 2. Productos con bajo desempeño comercial
        situations["productos_bajo_desempeno"] = []
        if producto_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]):
            agg_dict = {ventas_col: "sum"}
            if unidades_col and pd.api.types.is_numeric_dtype(df[unidades_col]):
                agg_dict[unidades_col] = "sum"
            if margen_col and pd.api.types.is_numeric_dtype(df[margen_col]):
                agg_dict[margen_col] = "mean"

            prod_stats = df.groupby(producto_col).agg(agg_dict)
            media_ventas = prod_stats[ventas_col].mean()

            for prod, row in prod_stats.iterrows():
                v_prod = float(row[ventas_col])
                m_prod = float(row[margen_col]) if margen_col in row else 0.0
                u_prod = int(row[unidades_col]) if unidades_col in row else 0

                if v_prod < (media_ventas * 0.7) or m_prod < 25.0:
                    situations["productos_bajo_desempeno"].append({
                        "producto": str(prod), "ventas": v_prod, "margen_promedio": m_prod, "unidades": u_prod
                    })
                    problems.append({
                        "id": f"SIT-02-PROD-{prod}",
                        "dimension": "Comercial / Portafolio",
                        "tipo": "Producto con bajo desempeño",
                        "nivel": "CRÍTICO" if m_prod < 15.0 or v_prod < (media_ventas * 0.4) else "ALERTA",
                        "titulo": f"Bajo Desempeño Comercial: '{prod}'",
                        "hallazgo": f"El producto '{prod}' registra ventas de ${v_prod:,.0f} USD (promedio: ${media_ventas:,.0f} USD) y un margen de {m_prod:.1f}%.",
                        "causa_probable": "Falta de diferenciación competitiva, rotación estancada o costos de adquisición desproporcionados.",
                        "accion": "Evaluar la rentabilidad marginal del producto, rediseñar su precio o considerar su reemplazo."
                    })

        # 3. Regiones con resultados inferiores a otras
        situations["regiones_inferiores"] = []
        if region_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]):
            reg_agg = {ventas_col: "sum"}
            if margen_col and pd.api.types.is_numeric_dtype(df[margen_col]):
                reg_agg[margen_col] = "mean"

            reg_stats = df.groupby(region_col).agg(reg_agg)
            v_max = reg_stats[ventas_col].max()
            reg_max_name = reg_stats[ventas_col].idxmax()

            for reg, row in reg_stats.iterrows():
                v_reg = float(row[ventas_col])
                m_reg = float(row[margen_col]) if margen_col in row else 0.0
                ratio = (v_reg / v_max) if v_max > 0 else 1.0

                if ratio < 0.55 or m_reg < 25.0:
                    situations["regiones_inferiores"].append({
                        "region": str(reg), "ventas": v_reg, "margen_promedio": m_reg,
                        "brecha_vs_lider_pct": (1.0 - ratio) * 100.0, "lider": str(reg_max_name)
                    })
                    problems.append({
                        "id": f"SIT-03-REG-{reg}",
                        "dimension": "Comercial / Territorial",
                        "tipo": "Región con resultados inferiores",
                        "nivel": "CRÍTICO" if m_reg < 20.0 else "ALERTA",
                        "titulo": f"Región con Resultados Rezago: '{reg}'",
                        "hallazgo": f"La región '{reg}' generó ${v_reg:,.0f} USD (un {(1.0 - ratio)*100:.1f}% menos que '{reg_max_name}') con un margen de {m_reg:.1f}%.",
                        "causa_probable": "Baja penetración de mercado o costos logísticos locales elevados.",
                        "accion": "Reestructurar los canales de venta en la región y renegociar costos de distribución."
                    })

        # 4. Canales que presentan reducción de ingresos
        situations["canales_reduccion"] = []
        if canal_col and period_col and ventas_col and pd.api.types.is_numeric_dtype(df[ventas_col]):
            canal_pivot = df.pivot_table(index=canal_col, columns=period_col, values=ventas_col, aggfunc="sum", fill_value=0)
            p_cols = list(canal_pivot.columns)

            if len(p_cols) >= 2:
                for canal, s_vals in canal_pivot.iterrows():
                    v_init = float(s_vals[p_cols[0]])
                    v_final = float(s_vals[p_cols[-1]])
                    v_prev = float(s_vals[p_cols[-2]])
                    var_ult = ((v_final - v_prev) / v_prev) * 100.0 if v_prev > 0 else 0.0
                    var_glob = ((v_final - v_init) / v_init) * 100.0 if v_init > 0 else 0.0

                    if var_ult < -2.0 or var_glob < -5.0:
                        situations["canales_reduccion"].append({
                            "canal": str(canal), "ventas_iniciales": v_init, "ventas_finales": v_final,
                            "variacion_global_pct": var_glob, "variacion_ultimo_pct": var_ult
                        })
                        problems.append({
                            "id": f"SIT-04-CANAL-{canal}",
                            "dimension": "Comercial / Canales",
                            "tipo": "Canal con reducción de ingresos",
                            "nivel": "CRÍTICO" if var_glob < -15.0 else "ALERTA",
                            "titulo": f"Contracción en Canal: '{canal}'",
                            "hallazgo": f"El canal '{canal}' cayó de ${v_init:,.0f} USD a ${v_final:,.0f} USD (Variación global: {var_glob:+.1f}%, último periodo: {var_ult:+.1f}%).",
                            "causa_probable": "Migración hacia otros canales o comisiones poco atractivas para intermediarios.",
                            "accion": "Diseñar paquetes de incentivos para el canal o canalizar inversión hacia los medios de mayor tracción."
                        })

        # 5. Cambios de precios asociados con variaciones de ventas
        situations["sensibilidad_precios"] = []
        active_precio = None
        if not precio_col and ventas_col and unidades_col:
            if pd.api.types.is_numeric_dtype(df[unidades_col]) and pd.api.types.is_numeric_dtype(df[ventas_col]):
                df["_precio_calc"] = np.where(df[unidades_col] > 0, df[ventas_col] / df[unidades_col], np.nan)
                active_precio = "_precio_calc"
        elif precio_col and pd.api.types.is_numeric_dtype(df[precio_col]):
            active_precio = precio_col

        if active_precio and period_col and (producto_col or region_col) and unidades_col:
            if pd.api.types.is_numeric_dtype(df[unidades_col]):
                group_key = producto_col or region_col
                for key_val, g_data in df.groupby(group_key):
                    p_grp = g_data.groupby(period_col, sort=False).agg({active_precio: "mean", unidades_col: "sum"})
                    if len(p_grp) >= 2:
                        p_keys = list(p_grp.index)
                        for i in range(1, len(p_keys)):
                            p0, p1 = p_keys[i-1], p_keys[i]
                            try:
                                pr0, pr1 = float(p_grp.loc[p0, active_precio]), float(p_grp.loc[p1, active_precio])
                                u0, u1 = float(p_grp.loc[p0, unidades_col]), float(p_grp.loc[p1, unidades_col])
                            except Exception:
                                continue

                            if pr0 > 0 and u0 > 0:
                                delta_p_pct = ((pr1 - pr0) / pr0) * 100.0
                                delta_u_pct = ((u1 - u0) / u0) * 100.0

                                if delta_p_pct >= 4.0 and delta_u_pct <= -8.0:
                                    situations["sensibilidad_precios"].append({
                                        "segmento": str(key_val), "periodo": f"{p0} -> {p1}",
                                        "variacion_precio_pct": delta_p_pct, "variacion_unidades_pct": delta_u_pct,
                                        "elasticidad": delta_u_pct / delta_p_pct if delta_p_pct != 0 else 0
                                    })
                                    problems.append({
                                        "id": f"SIT-05-PRECIO-{key_val}",
                                        "dimension": "Financiera / Pricing",
                                        "tipo": "Sensibilidad de precios vs ventas",
                                        "nivel": "ALERTA",
                                        "titulo": f"Sensibilidad Negativa de Precio: '{key_val}'",
                                        "hallazgo": f"En '{key_val}' ({p0} -> {p1}) el precio aumentó {delta_p_pct:+.1f}%, provocando una caída del {delta_u_pct:.1f}% en unidades vendidas.",
                                        "causa_probable": "Alta elasticidad precio de la demanda; existencia de sustitutos directos.",
                                        "accion": "Reevaluar la política de precios y complementar con ofertas de valor agregado."
                                    })
                                    break

        # 6. Productos con posibles dificultades de inventario
        situations["dificultades_inventario"] = []
        if stock_col and producto_col and unidades_col and pd.api.types.is_numeric_dtype(df[stock_col]):
            prod_inv = df.groupby(producto_col).agg({
                stock_col: ["min", "max", "mean"],
                unidades_col: "sum"
            })
            prod_inv.columns = ["stock_min", "stock_max", "stock_mean", "unidades_totales"]

            for prod, row in prod_inv.iterrows():
                st_min = float(row["stock_min"])
                st_max = float(row["stock_max"])
                u_tot = float(row["unidades_totales"])

                if st_min < 50 and u_tot > 500:
                    situations["dificultades_inventario"].append({
                        "producto": str(prod), "tipo_problema": "Riesgo de Quiebre de Stock",
                        "stock_minimo": st_min, "unidades_vendidas": u_tot
                    })
                    problems.append({
                        "id": f"SIT-06-STOCKOUT-{prod}",
                        "dimension": "Operativa / Inventarios",
                        "tipo": "Riesgo de quiebre de stock",
                        "nivel": "CRÍTICO",
                        "titulo": f"Riesgo Inminente de Quiebre de Stock: '{prod}'",
                        "hallazgo": f"El producto '{prod}' registró stock mínimo de solo {st_min:.0f} unidades, frente a una demanda de {u_tot:,.0f} unidades.",
                        "causa_probable": "Fallas en el punto de reorden con proveedores o tiempos de reposición lentos.",
                        "accion": "Incrementar el stock de seguridad y fijar alarmas automáticas de reaprovisionamiento."
                    })

                elif st_max > (u_tot * 1.5) and st_max > 1000:
                    situations["dificultades_inventario"].append({
                        "producto": str(prod), "tipo_problema": "Sobrestock / Capital Inmovilizado",
                        "stock_maximo": st_max, "unidades_vendidas": u_tot
                    })
                    problems.append({
                        "id": f"SIT-06-OVERSTOCK-{prod}",
                        "dimension": "Operativa / Inventarios",
                        "tipo": "Sobrestock y capital inmovilizado",
                        "nivel": "ALERTA",
                        "titulo": f"Sobrestock y Capital Atrapado: '{prod}'",
                        "hallazgo": f"El producto '{prod}' mantiene {st_max:,.0f} unidades en bodega, superando ampliamente las ventas ({u_tot:,.0f} unidades).",
                        "causa_probable": "Pronósticos de demanda optimistas o compras por lotes excesivos.",
                        "accion": "Implementar promociones de liquidación de inventario y pausar pedidos de reposición."
                    })

        self.detected_situations = situations
        self.problems = problems

    def _summarize_dimensions(self):
        """Genera resumen de estado para las dimensiones."""
        dims = {}
        for dim_key, dim_name in [
            ("financiera", "Financiera"),
            ("comercial", "Comercial"),
            ("operativa", "Operativa"),
            ("talento", "Talento Humano")
        ]:
            dim_probs = [p for p in self.problems if dim_name.lower() in p["dimension"].lower()]
            has_crit = any(p["nivel"] == "CRÍTICO" for p in dim_probs)
            has_alert = any(p["nivel"] == "ALERTA" for p in dim_probs)

            if has_crit:
                status = "CRÍTICO"
                color = "#EF4444"
            elif has_alert:
                status = "PRECAUCIÓN"
                color = "#F59E0B"
            else:
                status = "SALUDABLE"
                color = "#10B981"

            dims[dim_key] = {
                "name": dim_name,
                "status": status,
                "color": color,
                "problem_count": len(dim_probs)
            }

        self.dimensions_summary = dims
