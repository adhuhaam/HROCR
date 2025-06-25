import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PassportParser:
    def __init__(self):
        # Define regex patterns for passport fields
        self.patterns = {
            'passport_number': [
                r'Passport\s+No\.?\s*[:\-]?\s*([A-Z0-9]{6,15})',
                r'Document\s+No\.?\s*[:\-]?\s*([A-Z0-9]{6,15})',
                r'P<[A-Z]{3}([A-Z0-9]{9})',
                r'([A-Z]{1,3}[0-9]{6,10})',
                r'No\.?\s*[:\-]?\s*([A-Z0-9]{6,15})',
                r'Number[:\-\s]*([A-Z0-9]{6,15})',
                r'([0-9]{8,12})',
                r'OLD\s+PASSPORT\s+NO\.?\s*[:\-]?\s*([A-Z0-9]{6,15})',  # Previous passport
            ],
            'surname': [
                r'Surname[:\-\s]*([A-Z][A-Z\s]{1,30})(?:\s*\n|\s+[A-Z][a-z]|\s+GIVEN|\s+NAME)',
                r'Family\s+Name[:\-\s]*([A-Z][A-Z\s]{1,30})(?:\s*\n|\s+GIVEN)',
                r'([A-Z]{2,20}),\s*([A-Z\s]{2,30})',  # "SURNAME, GIVEN NAMES" format
                r'NAME[:\-\s]*([A-Z]{2,20})\s+([A-Z\s]{2,30})',
                r'([A-Z]{2,20})\s+[A-Z]{2,20}\s+[A-Z]{2,20}',  # First word of full name
            ],
            'given_names': [
                r'Given\s+Names?[:\-\s]*([A-Z][A-Z\s]{1,40})(?:\s*\n|\s+DATE|\s+NATIONALITY)',
                r'First\s+Name[:\-\s]*([A-Z][A-Z\s]{1,30})(?:\s*\n)',
                r'([A-Z]{2,20}),\s*([A-Z\s]{2,30})',  # Extract given names from "SURNAME, GIVEN" format
                r'NAME[:\-\s]*[A-Z]{2,20}\s+([A-Z\s]{2,30})',  # Second part of full name
                r'Father.*?Name[:\-\s]*([A-Z][A-Z\s]{1,30})(?:\s*\n)',
            ],
            'nationality': [
                r'Nationality[:\-\s]*([A-Z]{3,20})(?:\s*\n|\s+DATE)',
                r'Country[:\-\s]*([A-Z]{3,20})',
                r'P<([A-Z]{3})',
                r'([A-Z]{3})\s+NATIONALITY',
                r'BANGLADESH|INDIA|PAKISTAN|SRI\s+LANKA|NEPAL|UNITED\s+STATES|CANADA|AUSTRALIA',
            ],
            'date_of_birth': [
                r'Date\s+of\s+Birth[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'DOB[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'Born[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'Birth[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',  # Any date format
                r'([0-9]{2})\s*([0-9]{2})\s*([0-9]{4})',  # Spaced date format
            ],
            'place_of_birth': [
                r'Place\s+of\s+Birth[:\-\s]*([A-Z][A-Z\s,]{2,40})(?:\s*\n|\s+SEX|\s+DATE)',
                r'Born\s+in[:\-\s]*([A-Z][A-Z\s,]{2,40})(?:\s*\n)',
                r'Birth\s+Place[:\-\s]*([A-Z][A-Z\s,]{2,40})(?:\s*\n)',
            ],
            'sex': [
                r'Sex[:\-\s]*([MF])',
                r'Gender[:\-\s]*([MF])',
                r'([MF])\s*[0-9]{6}',
                r'MALE|FEMALE',
            ],
            'date_of_issue': [
                r'Date\s+of\s+Issue[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'Issue[d]?[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})\s*ISSUE',
            ],
            'date_of_expiry': [
                r'Date\s+of\s+Expiry[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'Expir[yies]*[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'Valid\s+until[:\-\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})',
                r'([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})\s*EXPIRY',
            ],
            'issuing_authority': [
                r'Issuing\s+Authority[:\-\s]*([A-Z][A-Z\s,]{5,50})(?:\s*\n|\s+DATE)',
                r'Authority[:\-\s]*([A-Z][A-Z\s,]{5,50})(?:\s*\n)',
                r'Department[:\-\s]*([A-Z][A-Z\s,]{5,50})(?:\s*\n)',
                r'DEPARTMENT\s+OF\s+PASSPORTS[A-Z\s,]*',
            ],
            'emergency_contact': [
                r'Emergency\s+Contact[:\-\s]*([A-Z][A-Z\s,]{5,50})(?:\s*\n|\s+[0-9])',
                r'Contact[:\-\s]*([A-Z][A-Z\s,]{5,50})(?:\s*\n)',
                r'In\s+case\s+of\s+emergency[:\-\s]*([A-Z][A-Z\s,]{5,50})(?:\s*\n)',
            ],
            'phone_number': [
                r'Phone[:\-\s]*([0-9\+\-\(\)\s]{8,20})',
                r'Tel[:\-\s]*([0-9\+\-\(\)\s]{8,20})',
                r'Mobile[:\-\s]*([0-9\+\-\(\)\s]{8,20})',
                r'([0-9]{3,4}[\-\s]?[0-9]{3,4}[\-\s]?[0-9]{3,6})',
                r'(\+[0-9]{1,3}[\-\s]?[0-9]{8,12})',
            ],
            'previous_passport': [
                r'Old\s+Passport\s+No[:\-\s]*([A-Z0-9]{6,15})',
                r'Previous\s+Passport[:\-\s]*([A-Z0-9]{6,15})',
                r'Last\s+Passport[:\-\s]*([A-Z0-9]{6,15})',
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
        
        # Fix common OCR errors for specific contexts
        # Don't replace numbers in passport numbers, dates, etc.
        # text = text.replace('0', 'O').replace('1', 'I')  # Disabled to preserve numbers
        
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
