"""
JSON Tools for Multi-Agent Demo
Provides JSON validation, file saving, file querying, and file deletion capabilities.
"""

import json
import os
from datetime import datetime
from typing import Optional
import uuid


# Storage directory for saved JSON files
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "saved_json_files")


def validate_json(json_string: str) -> str:
    """
    Validate JSON format and return error details if invalid.

    Args:
        json_string: The JSON string to validate

    Returns:
        Validation result with error details if invalid
    """
    try:
        # Try to parse the JSON
        parsed_data = json.loads(json_string)

        # Return success message with formatted JSON
        formatted_json = json.dumps(parsed_data, indent=2, ensure_ascii=False)
        return f"OK: JSON format valid\n\n```json\n{formatted_json}\n```"

    except json.JSONDecodeError as e:
        # Return detailed error information
        error_msg = f"Error: JSON format invalid\n\n"
        error_msg += f"- Line: {e.lineno}, Column: {e.colno}\n"
        error_msg += f"- Message: {e.msg}\n"

        # Show context around the error
        lines = json_string.split('\n')
        if e.lineno <= len(lines):
            error_line = lines[e.lineno - 1]
            error_msg += f"- Line content: `{error_line.strip()}`\n"

        return error_msg

    except Exception as e:
        return f"Error: Validation failed - {str(e)}"


def save_json_file(json_data: str) -> str:
    """
    Save validated JSON to local file with timestamp and unique ID.

    Args:
        json_data: The validated JSON data as string

    Returns:
        Saved filename information
    """
    try:
        # Ensure storage directory exists
        os.makedirs(STORAGE_DIR, exist_ok=True)

        # Parse JSON to ensure it's valid
        parsed_data = json.loads(json_data)

        # Generate timestamp and unique ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}.json"
        filepath = os.path.join(STORAGE_DIR, filename)

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)

        return f"OK: JSON file saved\n\nFilename: `{filename}`\nPath: `{STORAGE_DIR}`\nID: `{unique_id}`"

    except json.JSONDecodeError as e:
        return f"Error: Save failed - JSON format error - {e.msg}"
    except Exception as e:
        return f"Error: Save failed - {str(e)}"


def list_saved_files() -> str:
    """
    Query the list of saved JSON files in the storage directory.

    Returns:
        List of saved files (filenames only)
    """
    try:
        # Ensure storage directory exists
        os.makedirs(STORAGE_DIR, exist_ok=True)

        # List all JSON files
        files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.json')]

        if not files:
            return "No saved JSON files found\n\nUse save function to create new files."

        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(STORAGE_DIR, x)), reverse=True)

        result = f"Saved JSON files ({len(files)} files)\n\n"
        result += "\n".join(f"- `{filename}`" for filename in files)

        return result

    except Exception as e:
        return f"Error: Failed to list files - {str(e)}"


def get_file_detail(unique_id: str) -> str:
    """
    Query detailed content of a saved JSON file by unique ID.

    Args:
        unique_id: The unique ID portion of the filename

    Returns:
        Detailed file content
    """
    try:
        # Ensure storage directory exists
        os.makedirs(STORAGE_DIR, exist_ok=True)

        # Find the file by unique ID
        files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.json')]

        target_file = None
        for filename in files:
            if unique_id in filename:
                target_file = filename
                break

        if not target_file:
            available_ids = [f.replace('.json', '').split('_')[-1] for f in files]
            return f"Error: File with ID `{unique_id}` not found\n\nAvailable IDs:\n" + "\n".join(f"- `{uid}`" for uid in available_ids)

        filepath = os.path.join(STORAGE_DIR, target_file)

        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Get file info
        file_stat = os.stat(filepath)
        mod_time = datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        file_size = file_stat.st_size

        result = f"File Details: `{target_file}`\n\n"
        result += f"- ID: `{unique_id}`\n"
        result += f"- Modified: {mod_time}\n"
        result += f"- Size: {file_size} bytes\n\n"
        result += f"Content:\n\n```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```"

        return result

    except json.JSONDecodeError as e:
        return f"Error: Read failed - JSON format error - {e.msg}"
    except Exception as e:
        return f"Error: Read failed - {str(e)}"


def delete_json_file(unique_id: str) -> str:
    """
    Delete a JSON file by unique ID.

    Args:
        unique_id: The unique ID portion of the filename

    Returns:
        Deletion result
    """
    try:
        # Ensure storage directory exists
        os.makedirs(STORAGE_DIR, exist_ok=True)

        # Find the file by unique ID
        files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.json')]

        target_file = None
        for filename in files:
            if unique_id in filename:
                target_file = filename
                break

        if not target_file:
            available_ids = [f.replace('.json', '').split('_')[-1] for f in files]
            return f"Error: File with ID `{unique_id}` not found\n\nAvailable IDs:\n" + "\n".join(f"- `{uid}`" for uid in available_ids)

        filepath = os.path.join(STORAGE_DIR, target_file)

        # Delete the file
        os.remove(filepath)

        return f"OK: File deleted\n\nFilename: `{target_file}`\nID: `{unique_id}`"

    except Exception as e:
        return f"Error: Delete failed - {str(e)}"


def validate_and_save_json(json_data: str) -> str:
    """
    Validate JSON format and save to file - combined operation.

    Args:
        json_data: The JSON data to validate and save

    Returns:
        Save result with validation status and filename
    """
    try:
        # First validate
        validation_result = validate_json(json_data)
        if validation_result.startswith("Error:"):
            return validation_result

        # Then save
        return save_json_file(json_data)

    except Exception as e:
        return f"Error: Validation and save failed - {str(e)}"


def delete_file_by_id(unique_id: str) -> str:
    """
    Delete a JSON file by unique ID - wrapper function.

    Args:
        unique_id: The unique ID portion of the filename

    Returns:
        Deletion result
    """
    return delete_json_file(unique_id)
