import os
import pytesseract
from PIL import Image
import PyPDF2
import io
import logging


logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        # Configure Tesseract path if needed (for Raspberry Pi)
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        pass
    
    def process_file(self, filepath):
        """Process a file and extract text using OCR"""
        try:
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext == '.pdf':
                return self._process_pdf(filepath)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return self._process_image(filepath)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {str(e)}")
            raise
    
    def _process_image(self, image_path):
        """Extract text from image using Tesseract OCR"""
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image for better OCR results
            image = self._enhance_image(image)
            
            # Configure Tesseract for passport documents
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789<>/'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            raise
    
    def _process_pdf(self, pdf_path):
        """Extract text from PDF by converting to images first"""
        try:
            # Try to extract text directly first (for text-based PDFs)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # If we got meaningful text, return it
                if len(text.strip()) > 50:
                    return text.strip()
            
            # If direct text extraction failed, convert to images and use OCR
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, dpi=300)
                
                extracted_text = ""
                for i, image in enumerate(images):
                    # Enhance image for better OCR
                    enhanced_image = self._enhance_image(image)
                    
                    # Configure Tesseract
                    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789<>/'
                    
                    # Extract text from this page
                    page_text = pytesseract.image_to_string(enhanced_image, config=custom_config)
                    extracted_text += page_text + "\n"
                
                return extracted_text.strip()
                
            except ImportError:
                logger.error("pdf2image not available, falling back to PyPDF2 only")
                return text.strip() if text.strip() else "No text could be extracted from PDF"
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise
    
    def _enhance_image(self, image):
        """Enhance image for better OCR results"""
        try:
            from PIL import ImageEnhance, ImageFilter
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.SMOOTH_MORE)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error enhancing image: {str(e)}")
            return image  # Return original image if enhancement fails
