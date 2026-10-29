"""
main.py
Punto de entrada para la aplicación de Diagnóstico Empresarial Multidimensional.
"""
import sys
from app.ui.main_window import MainWindow

def main():
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()

