class Colors:
    BACKGROUND = "#180C1C"
    BACKGROUND_RGB = "24, 12, 28"
    SECONDARY = "#EDAE88"
    THIRD = "#FFD2C2"


class Styles:
    WINDOW_BAR_BUTTON = f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            padding: 5px;
            font-size: 16px;
        }}
        QPushButton:hover {{
            background-color: rgba(0, 0, 0, 0.1);
        }}
    """

    STATUS_WIDGET = f"""
        background-color: {Colors.BACKGROUND};
        border-radius: 5px;
    """

    STATUS_LABEL = f"""
        font-size: 18px;
        font-weight: bold;
        color: #d9534f;
    """

    STATS_WIDGET = f"""
        color: {Colors.THIRD};
        background-color: {Colors.BACKGROUND};
        border-radius: 5px;
    """

    IMAGE_BUTTON = f"""
        
    """

    MAIN_WIDGET = f"""
        background-color: {Colors.BACKGROUND};
    """

    TITLE_BAR = f"""
        font-size: 14px;
        font-weight: bold;
        color: {Colors.SECONDARY};
        background-color: transparent;
    """

    STATS_LABEL = f"""
        color: {Colors.SECONDARY};
        font-size: 12px;
    """

    STATS_VALUE = f"""
        color: {Colors.THIRD};
        font-size: 16px;
        font-weight: bold;
    """

    STATUS_ON = f"""
        font-size: 18px;
        font-weight: bold;
        color: #5cb85c;
    """

    STATUS_OFF = f"""
        font-size: 18px;
        font-weight: bold;
        color: #d9534f;
    """

    STATUS_STARTING = f"""
        font-size: 18px;
        font-weight: bold;
        color: #f0ad4e;
    """