"""
data_loader.py
Manejo robusto, inteligente y universal de carga de archivos Excel (.xlsx, .xls) y CSV.
Detecta automáticamente hojas con datos, encabezados desplazados, formatos numéricos y caracteres especiales.
"""
import os
import csv
import re
from typing import Optional, Tuple, Dict, Any, List

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False


class DataLoader:
    """Carga y procesa archivos de datos empresariales con soporte universal para Excel y CSV."""

    @staticmethod
    def load_file(file_path: str, sheet_name: Optional[str] = None) -> Tuple[bool, str, Optional[Any], Dict[str, Any]]:
        """
        Carga un archivo Excel o CSV con detección inteligente de estructura.
        
        Retorna:
            (éxito: bool, mensaje: str, data: DataFrame, metadata: dict)
        """
        if not os.path.exists(file_path):
            return False, "El archivo especificado no existe.", None, {}

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in [".csv", ".xlsx", ".xls", ".xlsm"]:
            return False, f"Formato no soportado: '{ext}'. Use .xlsx, .xls o .csv", None, {}

        file_size_kb = round(os.path.getsize(file_path) / 1024, 2)
        base_name = os.path.basename(file_path)

        metadata: Dict[str, Any] = {
            "file_name": base_name,
            "file_path": file_path,
            "file_size_kb": file_size_kb,
            "extension": ext,
            "sheet_name": None,
            "available_sheets": [],
            "rows": 0,
            "cols": 0,
            "columns": []
        }

        try:
            if PANDAS_AVAILABLE:
                return DataLoader._load_with_pandas(file_path, ext, metadata, sheet_name)
            else:
                return DataLoader._load_fallback(file_path, ext, metadata)
        except Exception as e:
            return False, f"Error al procesar el archivo: {str(e)}", None, metadata

    @staticmethod
    def _load_with_pandas(file_path: str, ext: str, metadata: Dict[str, Any], selected_sheet: Optional[str] = None):
        """Carga avanzada utilizando pandas con detección de encabezados y hojas."""
        df = None

        if ext == ".csv":
            # 1. CARGA DE CSV CON DETECCIÓN DE ENCODING Y DELIMITADOR
            encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252", "iso-8859-1"]
            delimiters = [",", ";", "\t", "|"]

            for enc in encodings:
                for sep in delimiters:
                    try:
                        temp_df = pd.read_csv(file_path, sep=sep, encoding=enc, nrows=10)
                        if len(temp_df.columns) > 1:
                            df = pd.read_csv(file_path, sep=sep, encoding=enc)
                            break
                    except Exception:
                        pass
                if df is not None:
                    break

            if df is None:
                try:
                    df = pd.read_csv(file_path, sep=None, engine="python", encoding="latin-1")
                except Exception:
                    df = pd.read_csv(file_path, encoding="utf-8", errors="replace")

        else:
            # 2. CARGA DE EXCEL (.xlsx, .xls, .xlsm)
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            metadata["available_sheets"] = sheets

            sheet_to_use = selected_sheet if (selected_sheet and selected_sheet in sheets) else None

            # Si no se especificó hoja, buscar la que tenga más datos
            if not sheet_to_use:
                best_sheet = sheets[0]
                max_score = -1

                for s in sheets:
                    try:
                        preview = excel_file.parse(s, nrows=25)
                        score = preview.shape[0] * preview.shape[1]
                        # Priorizar nombres típicos si hay empate
                        s_lower = s.lower()
                        if any(k in s_lower for k in ["dato", "venta", "data", "sheet1", "hoja1", "reporte"]):
                            score += 50
                        if score > max_score:
                            max_score = score
                            best_sheet = s
                    except Exception:
                        pass
                sheet_to_use = best_sheet

            metadata["sheet_name"] = sheet_to_use

            # Carga inicial de la hoja seleccionada
            df = excel_file.parse(sheet_to_use)

        # 3. DETECCIÓN INTELIGENTE DE ENCABEZADO REAL EN CASO DE FILAS VACÍAS O TÍTULOS
        df = DataLoader._smart_header_cleaning(df)

        # 4. LIMPIEZA GENERAL DEL DATAFRAME
        # Eliminar filas y columnas 100% vacías
        df = df.dropna(how="all").dropna(axis=1, how="all")

        # Normalizar nombres de columnas (eliminar espacios extras, convertir a str)
        clean_cols = []
        for i, col in enumerate(df.columns):
            c_str = str(col).strip()
            if not c_str or "unnamed:" in c_str.lower():
                c_str = f"Columna_{i+1}"
            clean_cols.append(c_str)
        df.columns = clean_cols

        # Si aún no tiene columnas o filas, avisar
        if df.empty or len(df.columns) == 0:
            return False, "El archivo o la hoja seleccionada no contiene registros válidos.", None, metadata

        metadata["rows"] = len(df)
        metadata["cols"] = len(df.columns)
        metadata["columns"] = list(df.columns)

        sheet_info = f" [Hoja: '{metadata['sheet_name']}']" if metadata.get("sheet_name") else ""
        return True, f"Archivo '{metadata['file_name']}'{sheet_info} cargado con éxito ({len(df):,} filas y {len(df.columns)} columnas).", df, metadata

    @staticmethod
    def _smart_header_cleaning(df: pd.DataFrame) -> pd.DataFrame:
        """
        Si la fila 1 es un título (ej. 'Reporte 2024') o casi todas las columnas son 'Unnamed:',
        busca en las primeras 8 filas la fila que contenga los nombres reales de columnas.
        """
        if df.empty:
            return df

        # Contar cuántas columnas son 'Unnamed'
        unnamed_count = sum(1 for c in df.columns if "unnamed:" in str(c).lower() or not str(c).strip())

        # Si más del 40% de las columnas son Unnamed, o si la primera fila parece encabezado
        if unnamed_count > len(df.columns) * 0.4:
            for r_idx in range(min(8, len(df))):
                row_vals = df.iloc[r_idx]
                valid_str_count = sum(1 for v in row_vals if pd.notnull(v) and str(v).strip() != "")
                # Si esta fila tiene nombres en la mayoría de sus celdas
                if valid_str_count >= max(2, len(df.columns) * 0.5):
                    new_headers = [str(v).strip() if pd.notnull(v) and str(v).strip() else f"Columna_{i+1}"
                                   for i, v in enumerate(row_vals)]
                    df = df.iloc[r_idx + 1:].copy()
                    df.columns = new_headers
                    df.reset_index(drop=True, inplace=True)
                    break

        return df

    @staticmethod
    def _load_fallback(file_path: str, ext: str, metadata: Dict[str, Any]):
        """Fallback cuando pandas no está presente."""
        if ext != ".csv":
            return False, "Para archivos Excel (.xlsx/.xls) se requiere pandas y openpyxl.", None, metadata

        rows = []
        with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
            sample = f.read(2048)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except Exception:
                dialect = csv.excel
            reader = csv.reader(f, dialect)
            header = [str(c).strip() for c in next(reader, [])]
            for row in reader:
                rows.append(row)

        metadata["rows"] = len(rows)
        metadata["cols"] = len(header)
        metadata["columns"] = header
        return True, "Archivo CSV cargado (Modo básico).", rows, metadata
