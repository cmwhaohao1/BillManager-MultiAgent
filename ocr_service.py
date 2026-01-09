"""
Simple OCR Service for Testing
Simulates OCR processing for financial documents.
"""

from flask import Flask, request, jsonify
import base64
from datetime import datetime

app = Flask(__name__)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "ocr"})


@app.route('/ocr', methods=['POST'])
def ocr():
    """OCR endpoint - simulates OCR processing."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        filename = file.filename

        # Read file content
        file_content = file.read()

        # Simulate OCR processing based on filename
        # In real implementation, this would call actual OCR API (like Tesseract, PaddleOCR, etc.)

        # Return mock OCR result
        mock_result = {
            "text": "Simulated OCR result for financial document",
            "amount": 125.50,
            "confidence": 0.95,
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }

        # Determine document type based on filename patterns
        filename_lower = filename.lower()
        if 'invoice' in filename_lower or 'fapiao' in filename_lower or '发票' in filename_lower:
            mock_result['type'] = 'invoice'
            mock_result['buyer'] = 'Company A'
            mock_result['seller'] = 'Company B'
            mock_result['summary'] = f"Buyer: Company A, Seller: Company B, Invoice Amount: {mock_result['amount']}RMB"
        elif 'receipt' in filename_lower or 'shouju' in filename_lower or '收据' in filename_lower:
            mock_result['type'] = 'expense'
            mock_result['summary'] = f"Supermarket shopping expense {mock_result['amount']}RMB"
        elif 'salary' in filename_lower or 'gongzi' in filename_lower or '工资' in filename_lower:
            mock_result['type'] = 'income'
            mock_result['summary'] = f"Salary income {mock_result['amount']}RMB"
        else:
            mock_result['type'] = 'unknown'
            mock_result['summary'] = f"Unknown {mock_result['amount']}RMB"

        print(f"[OCR] Processed file: {filename}")
        print(f"[OCR] Result: {mock_result}")

        return jsonify(mock_result)

    except Exception as e:
        print(f"[OCR] Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("[OCR Service] Starting on http://localhost:8080")
    print("[OCR Service] Health check: http://localhost:8080/health")
    app.run(host='0.0.0.0', port=8080, debug=True)
