"""Тонкий entry-point. Вся логика — в пакете ``agent_checker/``.

Запуск:
    python agent_checker.py
    # или
    python -m agent_checker
"""

from agent_checker.ui.app import main

if __name__ == '__main__':
    main()
