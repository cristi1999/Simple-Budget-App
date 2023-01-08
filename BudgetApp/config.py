import json



class Sounds:
    ADD_TRANSFER_SOUND = 'sounds/add_transfer.wav'
    EXIT_SOUND = 'sounds/exit_sound.wav'
    SELECT_OPTION_SOUND = 'sounds/select_option_sound.wav'
    START_SOUND = 'sounds/start_sound.wav'

class Colors:
    with open("colors.json", "r") as file:
        content = json.load(file)
    TRANSACTION_WIDGET_BACKGROUND = content["ColorTheme"]["TransactionWidgetBackground"]
    TRANSACTION_WIDGET_LABELS = content["ColorTheme"]["TransactionWidgetLabels"]
    TRANSACTION_WIDGET_INCOME = content["ColorTheme"]["TransactionWidgetIncome"]
    TRANSACTION_WIDGET_EXPENSE = content["ColorTheme"]["TransactionWidgetExpense"]
    OPERATIONS_WIDGET_COLOR=content["ColorTheme"]["OperationsWidgetColor"]
    TITLE_COLOR=content["ColorTheme"]["TitleColor"]
    SPECIAL_COLOR=content["ColorTheme"]["SpecialColor"]
    MENU_COLOR=content["ColorTheme"]["MenuColor"]
    INFO_COLOR=content["ColorTheme"]["InfoColor"]


