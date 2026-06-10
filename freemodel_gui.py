"""FreeModel.dev Account Manager — точка входа.

Запускается через run_freemodel.bat. Вся логика в пакете freemodel/.
"""

import sys

try:
    import tkinter as tk
except ImportError:
    tk = None

from freemodel.app import FreeModelGUI


def main():
    if tk is None:
        print("Ошибка: tkinter не установлен.")
        sys.exit(1)

    root = tk.Tk()
    app = FreeModelGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
