import os
import requests

from rites.logger import get_sec_logger

LOGGER = get_sec_logger("logs", log_name="Util")
def ensure_directory_exists(directory_path):
    """Ensure that the specified directory exists, creating it if necessary"""

    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            LOGGER.info(f"Created directory: {directory_path}")
        except Exception as e:
            LOGGER.error(f"Failed to create directory {directory_path}: {e}")
            return False
    return True


def fetch_tags(base_url="http://localhost:8000"):
    """Fetch all tags from the server API"""
    try:
        response = requests.get(f"{base_url}/tags")

        if response.status_code == 200:
            LOGGER.info(f"Successfully fetched {len(response.json())} tags from the server")
            return response.json()
        else:
            LOGGER.error(f"Failed to fetch tags. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        LOGGER.error(f"Error fetching tags: {e}")
        return None


def export_data_as_csv(suffix: str = "") -> bool:
    """Export tag data to CSV file"""
    if suffix:
        LOGGER.info(f"Exporting tag data to CSV with suffix: {suffix}...")
    else:
        LOGGER.info("Exporting tag data to CSV...")

    # Ensure data directory exists
    data_dir = "./data"
    if not ensure_directory_exists(data_dir):
        LOGGER.error("Failed to create data directory for auto-export")
        return False

    # Generate filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if suffix:
        export_path = f"{data_dir}/tags_export_{suffix}.csv"
    else:
        export_path = f"{data_dir}/tags_export_{timestamp}.csv"

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from server import Tag, DATABASE_URL

        # Create a database session
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # Get all tags from the database
        tags = db.query(Tag).all()

        # Convert SQLAlchemy objects to dictionaries
        tag_dicts = []
        for tag in tags:
            tag_dicts.append({
                "name": tag.name,
                "message": tag.message,
                "owner": tag.owner,
                "owner_id": tag.owner_id
            })

        # Export to CSV
        ret = True
        if tag_dicts:
            import csv
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = tag_dicts[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for tag in tag_dicts:
                    writer.writerow(tag)

            LOGGER.info(f"Successfully auto-exported {len(tag_dicts)} tags to {export_path}")
        else:
            LOGGER.info("No tags to export")
            ret = False

        # Close the session
        db.close()
        return ret
    except Exception as e:
        LOGGER.error(f"Failed to auto-export tags: {str(e)}")
        return False
