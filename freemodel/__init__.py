"""FreeModel.dev Account Manager — модульный пакет.

Главные компоненты:
- themes: 8 палитр (Light/Dark/Mocha/Nord/Solarized±/Dracula/GitHub)
- settings: загрузка/сохранение fm_settings.json
- account: класс FreeModelAccount + login/fetch
- browser_login: автоматическое получение cookie через Chrome/Edge/Playwright
- widgets: переиспользуемые виджеты (ToolTip, Toast, ResizableDialog)
- dialogs: диалоги добавления/редактирования аккаунтов
- app: главный класс FreeModelGUI
"""

__version__ = "2.0.0"
