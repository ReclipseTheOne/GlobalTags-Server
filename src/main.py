import uvicorn
import signal
import rites.logger as l
import argparse
import loggingHandler
import src.cfg as cfg
import atexit

from util import export_data_as_csv


# Rites Setup
LOGGER = l.get_logger("logs", log_name="FastAPI")
LOGGER.add_custom("critical_error", "CRR", 255, 40, 40)

# Import GUI app controller
try:
    from client.client import create_app, is_gui_available
    GUI_AVAILABLE = is_gui_available()
except ImportError as e:
    LOGGER.custom("critical_error", "GUI not available, resorting to headless mode. See error below\n", e)
    GUI_AVAILABLE = False


def run_server():
    """Function to run the server (used by both CLI and GUI)"""
    global server

    # Completely disable Uvicorn's logging
    LOGGER.info("Starting FastAPI server...")
    config = uvicorn.Config(
        "server:app",
        host=f"{cfg.get('host')}",
        port=int(cfg.get('port')),
        log_level="info",
        log_config=loggingHandler.get_logging_config()
    )
    server = uvicorn.Server(config)
    server.run()


def stop_server():
    """Function to stop the server gracefully"""
    global server
    if server:
        LOGGER.info("Stopping FastAPI server...")
        # Send SIGINT to the server
        server.handle_exit(signal.SIGINT, None)
        server = None
    else:
        LOGGER.warning("No server running to stop")


# Main
def main():
    atexit.register(export_data_as_csv, suffix="auto_export")

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="GlobalTags Server")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (CLI only)")
    args = parser.parse_args()

    # Check if we should run in headless mode
    if args.headless or not GUI_AVAILABLE:
        if args.headless:
            LOGGER.info("Starting in headless mode (--headless flag provided)...")
        elif not GUI_AVAILABLE:
            LOGGER.info("Starting in headless mode (GUI not available)...")
            LOGGER.info("Install PySide6 and psutil for GUI mode: pip install PySide6 psutil")
        run_server()
    else:
        # Start the GUI
        LOGGER.info("Starting in GUI mode...")
        app = create_app(run_server, stop_server)
        if app:
            exit_code = app.run()
            return exit_code
        else:
            LOGGER.error("Failed to create GUI application, falling back to headless mode")
            run_server()


if __name__ == "__main__":
    main()
