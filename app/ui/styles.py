"""
styles.py
Configuración visual, paleta corporativa moderna y estilos ttk para la aplicación.
"""

PALETTE = {
    # Fondos
    "bg_main": "#F8FAFC",          # Slate suave para el fondo general
    "bg_card": "#FFFFFF",          # Blanco para contenedores y tarjetas
    "bg_header": "#0F172A",        # Azul medianoche muy oscuro para encabezado
    "bg_dropzone": "#F1F5F9",      # Fondo de zona vacía
    
    # Textos
    "text_header": "#FFFFFF",      # Texto claro para header
    "text_primary": "#0F172A",     # Texto principal oscuro
    "text_secondary": "#475569",   # Texto secundario / subtítulos
    "text_muted": "#94A3B8",       # Texto atenuado
    
    # Acciones principales
    "btn_load": "#2563EB",         # Azul brillante para Cargar Archivo
    "btn_load_hover": "#1D4ED8",
    "btn_analyze": "#0D9488",      # Verde azulado / Teal profesional para Analizar
    "btn_analyze_hover": "#0F766E",
    "btn_delete": "#EF4444",       # Rojo suave para Borrar
    "btn_delete_hover": "#DC2626",
    
    # Bordes y acentos
    "border": "#E2E8F0",
    "border_focus": "#3B82F6",
    "accent_badge": "#EEF2FF",
    "accent_badge_text": "#4F46E5",
}

FONTS = {
    "title_main": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 11, "normal"),
    "section_title": ("Segoe UI", 13, "bold"),
    "btn": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10, "normal"),
    "body_bold": ("Segoe UI", 10, "bold"),
    "caption": ("Segoe UI", 9, "normal"),
    "mono": ("Consolas", 9, "normal"),
}

