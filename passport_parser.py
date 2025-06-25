import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PassportParser:
    def __init__(self):
        # Define regex patterns for passport fields
        self.patterns = {
            'passport_number': [
                r'Passport\s+No\.?\s*[:\-]?\s*([A-Z0-9]{6,12})',
                r'Document\s+No\.?\s*[:\-]?\s*([A-Z0-9]{6,12})',
                r'P<[A-Z]{3}([A-Z0-9]{9})',
                r'([A-Z]{1,2}[0-9]{6,8})',
            ],
            'surname': [
                r'Surname[:\-\s]*([A-Z\s]+?)(?:\n|Given|Name)',
                r'Family\s+Name[:\-\s]*([A-Z\s]+?)(?:\n|Given)',
                r'P<[A-Z]{3}([A-Z]+)<<',
            ],
            'given_names': [
                r'Given\s+Names?[:\-\s]*([A-Z\s]+?)(?:\n|Nationality|Date)',
                r'First\s+Name[:\-\s]*([A-Z\s]+?)(?:\n|Nationality|Date)',
                r'P<[A-Z]{3}[A-Z]+<<([A-Z<]+)',
            ],
            'nationality': [
                r'Nationality[:\-\s]*([A-Z\s]+?)(?:\n|Date|Sex)',
                r'Country\s+Code[:\-\s]*([A-Z]{3})',
                r'P<([A-Z]{3})',
            ],
            'date_of_birth': [
                r'Date\s+of\s+Birth[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
                r'DOB[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
                r'Born[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
                r'([0-9]{6})[MF]',
            ],
            'place_of_birth': [
                r'Place\s+of\s+Birth[:\-\s]*([A-Z\s,]+?)(?:\n|Sex|Date)',
                r'Born\s+in[:\-\s]*([A-Z\s,]+?)(?:\n|Sex|Date)',
            ],
            'sex': [
                r'Sex[:\-\s]*([MF])',
                r'Gender[:\-\s]*([MF])',
                r'[0-9]{6}([MF])',
            ],
            'date_of_issue': [
                r'Date\s+of\s+Issue[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
                r'Issued[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
            ],
            'date_of_expiry': [
                r'Date\s+of\s+Expiry[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
                r'Expires?[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
                r'Valid\s+until[:\-\s]*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
                r'[MF][0-9]{6}([0-9]{6})',
            ],
            'issuing_authority': [
                r'Issuing\s+Authority[:\-\s]*([A-Z\s,]+?)(?:\n|Date)',
                r'Authority[:\-\s]*([A-Z\s,]+?)(?:\n|Date)',
            ]
        }
    
    def parse_passport_text(self, text):
        """Parse extracted text and return structured passport data"""
        try:
            logger.debug(f"Parsing text: {text[:200]}...")
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            result = {}
            
            # Extract each field using regex patterns
            for field, patterns in self.patterns.items():
                value = self._extract_field(cleaned_text, patterns)
                result[field] = value
                logger.debug(f"Extracted {field}: {value}")
            
            # Post-process and validate extracted data
            result = self._post_process_data(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing passport text: {str(e)}")
            return {}
    
    def _clean_text(self, text):
        """Clean and normalize the extracted text"""
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Fix common OCR errors
        text = text.replace('0', 'O').replace('1', 'I')  # In names/text fields
        
        return text.strip()
    
    def _extract_field(self, text, patterns):
        """Extract a field using multiple regex patterns"""
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value and len(value) > 1:  # Basic validation
                        return self._clean_field_value(value)
            except Exception as e:
                logger.warning(f"Error with pattern {pattern}: {str(e)}")
                continue
        
        return None
    
    def _clean_field_value(self, value):
        """Clean individual field values"""
        # Remove extra spaces and special characters
        value = re.sub(r'\s+', ' ', value)
        value = value.replace('<', ' ').replace('>', ' ')
        value = value.strip()
        
        return value if value else None
    
    def _post_process_data(self, data):
        """Post-process and validate extracted data"""
        # Clean names
        if data.get('surname'):
            data['surname'] = self._clean_name(data['surname'])
        
        if data.get('given_names'):
            data['given_names'] = self._clean_name(data['given_names'])
        
        # Standardize dates
        for date_field in ['date_of_birth', 'date_of_issue', 'date_of_expiry']:
            if data.get(date_field):
                data[date_field] = self._standardize_date(data[date_field])
        
        # Clean nationality
        if data.get('nationality'):
            data['nationality'] = self._clean_nationality(data['nationality'])
        
        # Validate sex
        if data.get('sex'):
            data['sex'] = data['sex'].upper() if data['sex'].upper() in ['M', 'F'] else None
        
        return data
    
    def _clean_name(self, name):
        """Clean name fields"""
        if not name:
            return None
        
        # Remove non-alphabetic characters except spaces
        name = re.sub(r'[^A-Za-z\s]', '', name)
        # Normalize whitespace
        name = re.sub(r'\s+', ' ', name)
        # Title case
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name.strip() if name.strip() else None
    
    def _standardize_date(self, date_str):
        """Standardize date format"""
        if not date_str:
            return None
        
        # Try different date formats
        formats = ['%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d', '%Y/%m/%d']
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%d/%m/%Y')
            except ValueError:
                continue
        
        # If it's 6 digits (YYMMDD format common in MRZ)
        if len(date_str) == 6 and date_str.isdigit():
            try:
                year = int(date_str[:2])
                # Assume 20xx for years 00-30, 19xx for years 31-99
                year = 2000 + year if year <= 30 else 1900 + year
                month = int(date_str[2:4])
                day = int(date_str[4:6])
                
                parsed_date = datetime(year, month, day)
                return parsed_date.strftime('%d/%m/%Y')
            except ValueError:
                pass
        
        return date_str  # Return original if cannot parse
    
    def _clean_nationality(self, nationality):
        """Clean nationality field"""
        if not nationality:
            return None
        
        # Common nationality codes and their full names
        country_codes = {
            'USA': 'United States',
            'GBR': 'United Kingdom', 
            'CAN': 'Canada',
            'AUS': 'Australia',
            'DEU': 'Germany',
            'FRA': 'France',
            'IND': 'India',
            'CHN': 'China',
            'JPN': 'Japan',
            'RUS': 'Russia'
        }
        
        nationality = nationality.strip().upper()
        
        # If it's a 3-letter code, try to expand it
        if len(nationality) == 3 and nationality in country_codes:
            return country_codes[nationality]
        
        return nationality.title()
