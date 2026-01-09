"""
OCR Tools for Multi-Agent Demo
Provides OCR capability by calling local OCR service.
"""

import logging
import requests
import base64
import tempfile
import glob
import os
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

# OCR service configuration
OCR_SERVICE_URL = "http://192.168.40.42:8112/ocr"  # Local OCR service endpoint

# Temporary directory for storing uploaded files (same level as tools directory)
TEMP_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "temp_uploads")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)


def save_uploaded_file(filename: str, file_content: str) -> str:
    """
    Save uploaded file (base64 encoded) to temp_uploads directory.

    Args:
        filename: Name of the uploaded file
        file_content: Base64 encoded file content

    Returns:
        Success message
    """
    try:
        print(f"[SAVE FILE] Saving file: {filename}")
        print(f"[SAVE FILE] Content length: {len(file_content)}")
        print(f"[SAVE FILE] First 100 chars: {file_content[:100]}")
        
        # Decode base64 content
        decoded_content = base64.b64decode(file_content)
        
        print(f"[SAVE FILE] Decoded length: {len(decoded_content)}")

        # Save to temp_uploads directory
        file_path = Path(TEMP_UPLOAD_DIR) / filename
        with open(file_path, 'wb') as f:
            f.write(decoded_content)

        print(f"[SAVE FILE] Saved to: {file_path}")
        logger.info(f"Saved uploaded file: {filename} to {file_path}")
        import json
        return json.dumps({
            "success": True,
            "message": f"File saved to {file_path}"
        }, ensure_ascii=False)

    except Exception as e:
        print(f"[SAVE FILE ERROR] {e}")
        logger.error(f"Error saving file: {e}")
        import json
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


def find_and_read_file(filename: str) -> str:
    """
    Find and read an uploaded file from messaging mod's temp directory.

    The messaging mod automatically saves uploaded files to temp directories.
    This tool searches for the file and reads its content.

    Args:
        filename: Name of the uploaded file

    Returns:
        JSON string with file info (path, size, success status)
    """
    import json
    try:
        print(f"[FIND FILE] Searching for file: {filename}")
        logger.info(f"Searching for file: {filename}")

        file_path = None

        # Try all messaging mod temp directories
        temp_base = tempfile.gettempdir()
        temp_pattern = os.path.join(temp_base, "openagents_agent_*_threads_*")
        temp_dirs = glob.glob(temp_pattern)

        print(f"[FIND FILE] Found {len(temp_dirs)} temp directories")

        for temp_dir in temp_dirs:
            alt_path = Path(temp_dir) / filename
            if alt_path.exists():
                file_path = alt_path
                print(f"[FIND FILE] Found file in: {file_path}")
                logger.info(f"Found file in: {file_path}")
                break

        if not file_path:
            error_msg = f"File not found: {filename} (searched {len(temp_dirs)} temp directories)"
            print(f"[FIND FILE ERROR] {error_msg}")
            logger.error(error_msg)
            return json.dumps({"success": False, "error": error_msg}, ensure_ascii=False)

        # Read file content and get size
        with open(str(file_path), 'rb') as f:
            file_content = f.read()
            file_size = len(file_content)

        print(f"[FIND FILE] File size: {file_size} bytes")
        print(f"[FIND FILE] First 20 bytes (hex): {file_content[:20].hex()}")

        return json.dumps({
            "success": True,
            "filename": filename,
            "path": str(file_path),
            "size": file_size
        }, ensure_ascii=False)

    except Exception as e:
        error_msg = f"Error finding/reading file: {str(e)}"
        print(f"[FIND FILE ERROR] {error_msg}")
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg}, ensure_ascii=False)


def process_image_with_ocr(filename: str, storage_type: str = "cache") -> str:
    """
    Process uploaded image file with local OCR service.

    Args:
        filename: Name of uploaded file
        storage_type: Storage type (e.g., "cache")

    Returns:
        JSON string with OCR results or error message
    """
    try:
        print(f"[OCR TOOLS] Processing image with OCR: {filename} (storage: {storage_type})")
        logger.info(f"Processing image with OCR: {filename} (storage: {storage_type})")

        # Search for file in multiple possible locations:
        # 1. temp_uploads directory (tools directory) - if save_uploaded_file was called
        # 2. All messaging mod temp directories - where files are saved by default

        file_path = None

        # Try temp_uploads first
        uploads_path = Path(TEMP_UPLOAD_DIR) / filename
        if uploads_path.exists():
            file_path = uploads_path
            print(f"[OCR TOOLS] Found file in temp_uploads: {file_path}")
            logger.info(f"Found file in temp_uploads: {file_path}")

        # Try all messaging mod temp directories
        if not file_path:
            temp_base = tempfile.gettempdir()
            temp_pattern = os.path.join(temp_base, "openagents_agent_*_threads_*")
            temp_dirs = glob.glob(temp_pattern)

            print(f"[OCR TOOLS] Searching {len(temp_dirs)} temp directories for file: {filename}")

            for temp_dir in temp_dirs:
                alt_path = Path(temp_dir) / filename
                if alt_path.exists():
                    file_path = alt_path
                    print(f"[OCR TOOLS] Found file in temp directory: {file_path}")
                    logger.info(f"Found file in temp directory: {file_path}")
                    break

        if not file_path:
            error_msg = f"File not found: {filename} (searched in temp_uploads and {len(glob.glob(os.path.join(tempfile.gettempdir(), 'openagents_agent_*_threads_*')))} temp dirs)"
            print(f"[OCR TOOLS ERROR] {error_msg}")
            logger.error(error_msg)
            import json
            return json.dumps({"error": error_msg}, ensure_ascii=False)

        # Read file content
        with open(str(file_path), 'rb') as f:
            file_content = f.read()

        print(f"[OCR TOOLS] File size: {len(file_content)} bytes")
        print(f"[OCR TOOLS] Sending request to OCR service: {OCR_SERVICE_URL}")

        # Send to local OCR service (using 'image' parameter as per your test code)
        response = requests.post(
            OCR_SERVICE_URL,
            files={'image': (filename, file_content)},
            timeout=30
        )

        print(f"[OCR TOOLS] Response status: {response.status_code}")
        print(f"[OCR TOOLS] Response content: {response.text[:500]}")

        if response.status_code == 200:
            ocr_result = response.json()
            print(f"[OCR TOOLS] OCR processing successful")
            logger.info(f"OCR processing successful: {ocr_result}")

            # Return JSON string of the result
            import json
            return json.dumps(ocr_result, ensure_ascii=False)
        else:
            error_msg = f"OCR service error: {response.status_code}"
            print(f"[OCR TOOLS ERROR] {error_msg}")
            logger.error(error_msg)
            import json
            return json.dumps({
                "error": error_msg,
                "status_code": response.status_code
            }, ensure_ascii=False)

    except requests.exceptions.Timeout:
        error_msg = "Error: OCR service timeout after 30 seconds"
        logger.error(error_msg)
        import json
        return json.dumps({"error": error_msg}, ensure_ascii=False)
    except requests.exceptions.ConnectionError:
        error_msg = f"Error: Cannot connect to OCR service at {OCR_SERVICE_URL}"
        logger.error(error_msg)
        import json
        return json.dumps({"error": error_msg}, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Error: OCR processing failed - {str(e)}"
        logger.error(error_msg)
        import json
        return json.dumps({"error": error_msg}, ensure_ascii=False)

