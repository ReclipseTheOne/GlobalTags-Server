from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit, QGridLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QTimer
import rites.logger as l

from .styles import Styles
from .widgets.ImageButton import ImageButton

from .widgets.ServerStatItem import ServerStatItem
from .widgets.CustomTitleBar import CustomTitleBar

import threading
import os
import sys
import time
import psutil

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGGER = l.get_sec_logger("logs", log_name="GUI")


class ServerManagerGUI(QMainWindow):
    """Main window for the Tag Server Manager GUI application"""

    # Define signals for thread-safe GUI updates
    status_changed = Signal(str)

    def __init__(self, run_server_func, stop_server_func=None):
        super().__init__(None, Qt.FramelessWindowHint)
        self.run_server_func = run_server_func
        self.stop_server_func = stop_server_func
        self.server_thread = None
        self.server_running = False
        self.server_process = None

        self.setWindowTitle("Tag Server Manager")
        self.setGeometry(100, 100, 600, 350)  # Smaller window size
        self.setup_ui()

        # Connect signals
        self.status_changed.connect(self.update_status)

        # Setup timer for stats update
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(2000)  # Update every 2 seconds

    def setup_ui(self):
        """Set up the user interface components"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_widget.setStyleSheet(Styles.MAIN_WIDGET)

        # Add custom title bar
        self.title_bar = CustomTitleBar(parent=self)
        self.title_bar.minimizeClicked.connect(self.showMinimized)
        self.title_bar.closeClicked.connect(self.close)
        main_layout.addWidget(self.title_bar)

        # Status section
        status_widget = QWidget()
        status_widget.setStyleSheet(Styles.STATUS_WIDGET)
        status_layout = QVBoxLayout(status_widget)

        # Server status label
        self.status_label = QLabel("Server Status: Offline")
        self.status_label.setStyleSheet(Styles.STATUS_LABEL)
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_widget)

        # Stats section
        stats_widget = QWidget()
        stats_widget.setStyleSheet(Styles.STATS_WIDGET)
        stats_layout = QGridLayout(stats_widget)

        # Create stat items
        self.uptime_stat = ServerStatItem("Uptime")
        stats_layout.addWidget(self.uptime_stat, 0, 0)

        self.cpu_stat = ServerStatItem("CPU Usage")
        stats_layout.addWidget(self.cpu_stat, 0, 1)

        self.memory_stat = ServerStatItem("Memory Usage")
        stats_layout.addWidget(self.memory_stat, 0, 2)

        self.requests_stat = ServerStatItem("Requests Handled")
        stats_layout.addWidget(self.requests_stat, 1, 0)

        self.tags_stat = ServerStatItem("Total Tags")
        stats_layout.addWidget(self.tags_stat, 1, 1)

        self.endpoints_stat = ServerStatItem("Active Endpoints")
        stats_layout.addWidget(self.endpoints_stat, 1, 2)

        main_layout.addWidget(stats_widget)

        # Button layout
        button_layout = QGridLayout()
        button_layout.setSpacing(10)

        # Start button
        self.power_button = ImageButton("off_button", parent=self, size=(32, 32))
        self.power_button.clicked.connect(self.switch_power)
        button_layout.addWidget(self.power_button, 0, 0)

        # Open Logs button
        self.logs_button = ImageButton("logs_button", parent=self, size=(32, 32))
        self.logs_button.clicked.connect(self.open_logs)
        button_layout.addWidget(self.logs_button, 0, 2)

        main_layout.addLayout(button_layout)
        self.setCentralWidget(main_widget)

        # Start time tracking
        self.server_start_time = None

    def update_status(self, status):
        """Update the status label with the given status text"""
        if "Online" in status:
            self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #5cb85c;")
        elif "Starting" in status:
            self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f0ad4e;")
        else:
            self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d9534f;")

        self.status_label.setText(status)

    def open_logs(self):
        """Open the logs/latest.log file with the default system application"""
        log_path = os.path.abspath("logs/latest.log")

        if not os.path.exists(log_path):
            LOGGER.warning(f"Log file not found: {log_path}")
            return

        try:
            # Open with default application based on operating system
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(('open', log_path))
            elif os.name == 'nt':  # Windows
                os.startfile(log_path)
            elif os.name == 'posix':  # Linux
                subprocess.call(('xdg-open', log_path))

            LOGGER.debug(f"Opened log file: {log_path}")
        except Exception as e:
            LOGGER.error(f"Failed to open log file: {str(e)}")

    def start_server(self):
        """Start the server in a separate thread"""
        if self.server_running:
            return

        LOGGER.info("Starting server from GUI...")
        self.status_changed.emit("Server Status: Starting...")

        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self._run_server_thread)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.server_running = True
        self.server_start_time = time.time()
        self.power_button.change_icon("on_button")

    def switch_power(self):
        """Switch the power state of the server"""
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

    def _run_server_thread(self):
        """Run the server in a thread"""
        try:
            self.status_changed.emit("Server Status: Online")
            LOGGER.info("Server is now online!")

            # Get the current process
            self.server_process = psutil.Process(os.getpid())

            # Start the actual server
            self.run_server_func()
        except Exception as e:
            self.status_changed.emit(f"Server Status: Error - {str(e)}")
            LOGGER.error(f"Server error: {str(e)}")
            self.server_running = False
            self.server_start_time = None
            self.power_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def stop_server(self):
        """Stop the server"""
        if not self.server_running:
            return

        LOGGER.info("Stopping server from GUI...")
        self.status_changed.emit("Server Status: Stopping...")

        # Call the stop function if provided
        if self.stop_server_func:
            try:
                self.stop_server_func()
            except Exception as e:
                LOGGER.error(f"Failed to stop server gracefully: {str(e)}")

        self.server_running = False
        self.server_start_time = None
        self.status_changed.emit("Server Status: Offline")
        LOGGER.info("Server has been stopped")
        self.power_button.change_icon("off_button")

    def update_stats(self):
        """Update server statistics display"""
        if not self.server_running or not self.server_process:
            # Reset stats if server is not running
            self.uptime_stat.update_value("N/A")
            self.cpu_stat.update_value("N/A")
            self.memory_stat.update_value("N/A")
            self.requests_stat.update_value("N/A")
            self.tags_stat.update_value("N/A")
            self.endpoints_stat.update_value("N/A")
            return

        try:
            # Uptime
            if self.server_start_time:
                uptime_seconds = int(time.time() - self.server_start_time)
                hours, remainder = divmod(uptime_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                self.uptime_stat.update_value(uptime_str)

            # CPU and Memory
            cpu_percent = self.server_process.cpu_percent(interval=0.1)
            self.cpu_stat.update_value(f"{cpu_percent:.1f}%")

            memory_info = self.server_process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            self.memory_stat.update_value(f"{memory_mb:.1f} MB")

            # These would need to be implemented with actual server metrics
            # For now we'll just show placeholders
            self.requests_stat.update_value("--")

            # You could implement these by querying your database
            # self.tags_stat.update_value(str(count_tags()))
            self.tags_stat.update_value("--")

            # For FastAPI you could potentially get this from the app object
            self.endpoints_stat.update_value("4")  # Hardcoded based on your API endpoints

        except Exception as e:
            LOGGER.warning(f"Failed to update stats: {str(e)}")


class LogHandler:
    """Custom log handler that redirects logs to the GUI"""

    def __init__(self, gui):
        self.gui = gui

    def emit(self, record):
        """Emit a log record to the GUI"""
        log_entry = self.format(record)
        self.gui.append_log(log_entry)
