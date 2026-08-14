import cv2
import easyocr
import re
import hashlib
import os
from datetime import datetime

def process_dmart_bill(image_path):
    """
    Processes a supermarket bill image to extract the bill number, date, and total amount.
    Validates the store name and generates a cryptographic hash for fraud detection.
    """
    result = {
        "status": "error",
        "message": "",
        "date": None,
        "bill_number": None,
        "amount": None,
        "hash": None,
        "raw_text": ""
    }

    # Initialize the OCR engine
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        result["message"] = "Error: Image not found!"
        return result

    # Convert to grayscale for better contrast during text extraction
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ocr_results = reader.readtext(gray_image)

    # Concatenate extracted text blocks into a single uppercase string
    extracted_text_blocks = [text for (bbox, text, prob) in ocr_results]
    full_text = " ".join(extracted_text_blocks).upper()
    
    # PRE-PROCESSING: Remove timestamps (e.g., 17:07:59.532092) from the raw text 
    # immediately to prevent them from being mistakenly identified as the total amount.
    full_text = re.sub(r'\d{2}:\d{2}:\d{2}(?:[.,]\d+)?', '', full_text)
    result["raw_text"] = full_text

    # 1. STORE VALIDATION GUARD
    # Strip all non-alphabetic characters to cleanly check the store name
    cleaned_text = re.sub(r'[^A-Z]', '', full_text)
    if "ABCSUPERMARKET" not in cleaned_text:
        result["status"] = "rejected"
        result["message"] = "Fraud Alert: Not an ABC Supermarket bill."
        return result

    result["status"] = "accepted"

    # 2. EXTRACT BILL NUMBER
    # Captures digits following the 'BILL NO' keyword
    bill_match = re.search(r'BILL\s*NO[^\d]*(\d+)', full_text)
    if bill_match:
        result["bill_number"] = bill_match.group(1)

    # 3. EXTRACT AND STANDARDIZE DATE
    # Captures standard date formats and reformats them to DD/MM/YYYY for the hash
    date_match = re.search(r'DATE[^\d]*(\d{4}[/.-]\d{2}[/.-]\d{2}|\d{2}[/.-]\d{2}[/.-]\d{4})', full_text)
    if not date_match:
        date_match = re.search(r'(\d{4}[/.-]\d{2}[/.-]\d{2}|\d{2}[/.-]\d{2}[/.-]\d{4})', full_text)
        
    if date_match:
        raw_date = date_match.group(1)
        try:
            if "-" in raw_date and len(raw_date.split("-")[0]) == 4:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
            else:
                parsed_date = datetime.strptime(raw_date.replace("-", "/").replace(".", "/"), "%d/%m/%Y")
            result["date"] = parsed_date.strftime("%d/%m/%Y")
        except:
            result["date"] = raw_date

    # 4. EXTRACT TOTAL AMOUNT (Strictly look for TOTAL or PAID lines)
    # This ensures we grab the final grand total and completely ignore item prices and timestamps.
    amount_match = re.search(r'(?:TOTAL|PAID)[^\d]*(\d+[.,]\d{2})', full_text)
    
    if amount_match:
        result["amount"] = amount_match.group(1).replace(',', '.')
    else:
        # Fallback if keyword is missed
        all_prices = re.findall(r'(?<!\d)\d{1,5}[.,]\d{2}(?!\d)', full_text)
        if all_prices:
            clean_prices = [float(p.replace(',', '.')) for p in all_prices]
            result["amount"] = f"{max(clean_prices):.2f}"
        else:
            result["amount"] = "0.00"

    # 5. GENERATE SECURITY HASH
    # Creates a SHA-256 hash using the bill number and date for database cross-referencing
    if result["bill_number"] and result["date"]:
        unique_string = f"{result['bill_number']}_{result['date']}"
        result["hash"] = hashlib.sha256(unique_string.encode()).hexdigest()
        result["message"] = "Extracted successfully."
    else:
        result["message"] = "Could not clearly extract bill number or date."

    return result