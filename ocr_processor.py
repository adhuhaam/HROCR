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
        """Extract text from image using enhanced Tesseract OCR"""
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image for better OCR results
            enhanced_image = self._enhance_image(image)
            
            # Use optimized Tesseract configuration for passport documents
            config = r'--oem 3 --psm 3 -c preserve_interword_spaces=1'
            
            # Extract text using optimized Tesseract
            text = pytesseract.image_to_string(enhanced_image, config=config, lang='eng')
            
            logger.debug(f"Tesseract OCR result: {text[:200]}...")
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
                    
                    # Use enhanced OCR processing for each page
                    # Try multiple configurations to get best results
                    configs = [
                        r'--oem 3 --psm 6',
                        r'--oem 3 --psm 4',
                        r'--oem 3 --psm 3'
                    ]
                    
                    best_page_text = ""
                    max_conf = 0
                    
                    for config in configs:
                        try:
                            data = pytesseract.image_to_data(enhanced_image, config=config, output_type=pytesseract.Output.DICT)
                            text_parts = []
                            total_conf = 0
                            word_count = 0
                            
                            for j, conf in enumerate(data['conf']):
                                if int(conf) > 30:
                                    word = data['text'][j].strip()
                                    if word:
                                        text_parts.append(word)
                                        total_conf += int(conf)
                                        word_count += 1
                            
                            if word_count > 0:
                                avg_conf = total_conf / word_count
                                current_text = ' '.join(text_parts)
                                if avg_conf > max_conf:
                                    max_conf = avg_conf
                                    best_page_text = current_text
                                    
                        except Exception:
                            continue
                    
                    page_text = best_page_text or pytesseract.image_to_string(enhanced_image)
                    extracted_text += page_text + "\n"
                
                return extracted_text.strip()
                
            except ImportError:
                logger.error("pdf2image not available, falling back to PyPDF2 only")
                return text.strip() if text.strip() else "No text could be extracted from PDF"
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise
    
    def _enhance_image(self, image):
        """Enhance image for better OCR results with advanced preprocessing"""
        try:
            from PIL import ImageEnhance, ImageFilter, ImageOps
            import numpy as np
            
            # Resize image if too small (minimum 300 DPI equivalent)
            width, height = image.size
            if width < 1200 or height < 800:
                scale_factor = max(1200 / width, 800 / height)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.LANCZOS)
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Apply Gaussian blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Enhance contrast more aggressively
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.5)
            
            # Auto-level (histogram equalization)
            image = ImageOps.autocontrast(image, cutoff=2)
            
            # Sharpen the image
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            # Apply unsharp mask filter for better text clarity
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Convert to numpy array for morphological operations
            img_array = np.array(image)
            
            # Apply threshold to create binary image
            threshold = np.percentile(img_array, 60)  # Adaptive threshold
            img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
            
            # Convert back to PIL Image
            image = Image.fromarray(img_array, mode='L')
            
            return image
            
        except Exception as e:
            logger.warning(f"Error enhancing image: {str(e)}")
            return image  # Return original image if enhancement fails
