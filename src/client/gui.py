from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit, QGridLayout
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
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.run_server_func = run_server_func
        self.stop_server_func = stop_server_func
        self.server_thread = None
        self.server_running = False
        self.server_process = None

        self.setWindowTitle("GlobalTags Server")
        self.setGeometry(100, 100, 800, 500)
        self.setup_ui()

        # Connect signals
        self.status_changed.connect(self.update_status)

        # Setup timer for stats update
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(2000)  # Update every 2 seconds

    def setup_ui(self):
        "Shouldn't be called more than once"

        # ------------- WINDOW DEFINE START -------------

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)

        # Add custom title bar
        self.title_bar = CustomTitleBar("GlobalTags Server", self)
        self.title_bar.closeClicked.connect(self.close)
        self.title_bar.minimizeClicked.connect(self.showMinimized)
        main_layout.addWidget(self.title_bar)

        # Status section
        status_widget = QWidget()
        status_widget.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")
        status_layout = QVBoxLayout(status_widget)

        # Server status label
        self.status_label = QLabel("Server Status: Offline")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d9534f;")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_widget)

        # Stats section
        stats_widget = QWidget()
        stats_widget.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")
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

        # Log display
        log_label = QLabel("Server Logs")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(log_label)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: #272822; color: #f8f8f2; font-family: monospace;")
        self.log_display.setMinimumHeight(200)
        main_layout.addWidget(self.log_display)

        # Button layout
        button_layout = QGridLayout()
        button_layout.setSpacing(10)

        # Power Button
        self.power_button = ImageButton("src/resources/off_button", size=(16, 16))
        self.power_button.clicked.connect(self.switch_power)

        button_layout.addWidget(self.power_button, 0, 0)

        # ------------- WINDOW DEFINE END -------------

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

    def append_log(self, message):
        """Append a message to the log display"""
        self.log_display.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_server(self):
        """Start the server in a separate thread"""
        if self.server_running:
            return

        LOGGER.info("Starting server from GUI...")
        self.status_changed.emit("Server Status: Starting...")
        self.append_log("[INFO] Starting FastAPI server...")

        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self._run_server_thread)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.server_running = True
        self.server_start_time = time.time()
        self.power_button.change_icon("src/resources/on_button")

    def stop_server(self):
        """Stop the server"""
        if not self.server_running:
            return

        LOGGER.info("Stopping server from GUI...")
        self.status_changed.emit("Server Status: Stopping...")
        self.append_log("[INFO] Stopping FastAPI server...")

        # Call the stop function if provided
        if self.stop_server_func:
            try:
                self.stop_server_func()
            except Exception as e:
                self.append_log(f"[ERROR] Failed to stop server gracefully: {str(e)}")

        self.server_running = False
        self.server_start_time = None
        self.status_changed.emit("Server Status: Offline")
        self.append_log("[INFO] Server has been stopped")
        self.power_button.change_icon("src/resources/off_button")

    def _run_server_thread(self):
        """Run the server in a thread"""
        try:
            self.status_changed.emit("Server Status: Online")
            self.append_log("[SUCCESS] Server is now online!")

            # Get the current process
            self.server_process = psutil.Process(os.getpid())

            # Start the actual server
            self.run_server_func()
        except Exception as e:
            self.status_changed.emit(f"Server Status: Error - {str(e)}")
            self.append_log(f"[ERROR] {str(e)}")
            self.server_running = False
            self.server_start_time = None
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def switch_power(self):
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

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
            self.append_log(f"[WARNING] Failed to update stats: {str(e)}")


class LogHandler:
    """Custom log handler that redirects logs to the GUI"""

    def __init__(self, gui):
        self.gui = gui

    def emit(self, record):
        """Emit a log record to the GUI"""
        log_entry = self.format(record)
        self.gui.append_log(log_entry)
