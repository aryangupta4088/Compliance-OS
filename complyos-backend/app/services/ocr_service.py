import pytesseract
from PIL import Image
import io

class OCRService:
    @staticmethod
    def extract_text(image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to grayscale for better accuracy
            if image.mode != 'L':
                image = image.convert('L')
                
            text = pytesseract.image_to_string(image, lang='eng+hin')
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
