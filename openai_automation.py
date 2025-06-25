import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIAutomation:
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("OpenAI API key not found. AI automation features disabled.")
    
    def enhance_passport_extraction(self, raw_text, extracted_data):
        """Use OpenAI to improve passport data extraction accuracy"""
        if not self.enabled:
            return extracted_data
        
        try:
            prompt = f"""
            You are an expert passport data extraction assistant. Analyze the OCR text below and extract accurate passport information.
            
            OCR Text:
            {raw_text}
            
            Current extracted data:
            {json.dumps(extracted_data, indent=2)}
            
            Please provide improved extraction in JSON format with these exact fields:
            - passport_number: string (passport document number)
            - surname: string (family name/last name)
            - given_names: string (first and middle names)
            - nationality: string (country of citizenship)
            - date_of_birth: string (DD/MM/YYYY format)
            - place_of_birth: string (city, country)
            - sex: string (M or F)
            - date_of_issue: string (DD/MM/YYYY format)
            - date_of_expiry: string (DD/MM/YYYY format)
            - issuing_authority: string (government department that issued passport)
            - emergency_contact: string (emergency contact person name)
            - phone_number: string (contact phone number)
            - previous_passport: string (old passport number if mentioned)
            
            Rules:
            1. Only extract information that is clearly visible in the text
            2. Use null for missing information
            3. Standardize dates to DD/MM/YYYY format
            4. Clean up OCR errors in names and text
            5. Preserve original spelling of proper names
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a passport data extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            enhanced_data = json.loads(response.choices[0].message.content)
            logger.info("OpenAI enhanced passport data extraction completed")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"OpenAI enhancement failed: {str(e)}")
            return extracted_data
    
    def validate_passport_data(self, data):
        """Use OpenAI to validate passport data for consistency and errors"""
        if not self.enabled:
            return {"valid": True, "issues": []}
        
        try:
            prompt = f"""
            Analyze this passport data for consistency and potential errors:
            
            {json.dumps(data, indent=2)}
            
            Check for:
            1. Date format consistency (should be DD/MM/YYYY)
            2. Logical date relationships (birth < issue < expiry)
            3. Name format consistency
            4. Passport number format validity
            5. Missing critical information
            6. OCR errors or suspicious values
            
            Return JSON with:
            - valid: boolean (true if data appears correct)
            - issues: array of strings describing any problems found
            - suggestions: array of strings with improvement recommendations
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a passport data validator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            validation = json.loads(response.choices[0].message.content)
            return validation
            
        except Exception as e:
            logger.error(f"OpenAI validation failed: {str(e)}")
            return {"valid": True, "issues": []}
    
    def generate_document_content(self, passport_data, document_type="job_offer"):
        """Generate document content using passport data"""
        if not self.enabled:
            return None
        
        try:
            if document_type == "job_offer":
                prompt = f"""
                Create a professional job offer letter using this passport information:
                
                {json.dumps(passport_data, indent=2)}
                
                Generate a complete, professional job offer letter that:
                1. Uses the person's correct name from passport
                2. References their nationality and passport details for verification
                3. Includes standard employment terms placeholders
                4. Maintains professional business format
                5. Includes verification sections for passport validity
                
                Make it ready for HR use with placeholder fields like [POSITION], [SALARY], [START_DATE] that can be filled in.
                """
            else:
                prompt = f"Generate a {document_type} document using passport data: {json.dumps(passport_data, indent=2)}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional document generator. Create formal business documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI document generation failed: {str(e)}")
            return None
    
    def smart_field_correction(self, field_name, current_value, context):
        """Use OpenAI to suggest corrections for specific fields"""
        if not self.enabled:
            return current_value
        
        try:
            prompt = f"""
            Correct this passport field based on context:
            
            Field: {field_name}
            Current Value: {current_value}
            Context: {context}
            
            Provide the corrected value considering:
            1. Common OCR errors (0/O, 1/I, etc.)
            2. Proper formatting for the field type
            3. Logical consistency
            
            Return only the corrected value, nothing else.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data correction specialist. Return only the corrected value."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            corrected = response.choices[0].message.content.strip()
            return corrected if corrected else current_value
            
        except Exception as e:
            logger.error(f"OpenAI field correction failed: {str(e)}")
            return current_value