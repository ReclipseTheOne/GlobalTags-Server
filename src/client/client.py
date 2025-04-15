import rites.logger as l
from client.gui import ServerManagerGUI
import sys
import os

LOGGER = l.get_sec_logger("logs", log_name="Client")
LOGGER.add_custom("critical_error", "CRR", 255, 40, 40)

try:
    from PySide6.QtWidgets import QApplication
    import psutil  # Also check for psutil which we use for stats

    GUI_AVAILABLE = True
except ImportError as e:
    GUI_AVAILABLE = False
    LOGGER.custom("critical_eroor", "GUI not available, resorting to headless mode. See error below:\n", e)


# Add parent directory to path so we can import modules from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ServerManagerApp:
    """Main application class for the Tag Server Manager"""

    def __init__(self, run_server_func, stop_server_func=None):
        """
        Initialize the application

        Args:
            run_server_func: Function to call to start the server
            stop_server_func: Function to call to stop the server (optional)
        """
        self.app = QApplication([])
        self.window = ServerManagerGUI(run_server_func, stop_server_func)

    def run(self):
        """Run the application"""
        self.window.show()
        return self.app.exec()


def is_gui_available():
    """Check if GUI libraries are available"""
    return GUI_AVAILABLE


def create_app(run_server_func, stop_server_func=None):
    """Create and return a ServerManagerApp instance"""
    if not is_gui_available():
        LOGGER.warning("PySide6 or psutil not installed, GUI mode will not be available")
        return None

    try:
        return ServerManagerApp(run_server_func, stop_server_func)
    except Exception as e:
        LOGGER.error(f"Failed to create GUI application: {e}")
        return None
