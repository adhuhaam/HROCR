import os
import json
import logging
from datetime import datetime, timedelta
from openai_automation import OpenAIAutomation
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

class HRAutomation:
    def __init__(self):
        self.ai = OpenAIAutomation()
        self.sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        self.company_email = os.environ.get('COMPANY_EMAIL', 'hr@company.com')
        self.company_name = os.environ.get('COMPANY_NAME', 'Your Company')
        
    def send_offer_letter_email(self, passport_record, position_details):
        """Automatically email offer letter to candidate"""
        if not self.sendgrid_key:
            return {"success": False, "error": "SendGrid API key not configured"}
        
        try:
            # Generate personalized offer letter content
            if self.ai.enabled:
                offer_content = self.ai.generate_document_content({
                    'full_name': f"{passport_record.given_names} {passport_record.surname}",
                    'passport_number': passport_record.passport_number,
                    'nationality': passport_record.nationality,
                    'position': position_details.get('position', '[Position]'),
                    'salary': position_details.get('salary', '[Salary]'),
                    'start_date': position_details.get('start_date', '[Start Date]'),
                    'department': position_details.get('department', '[Department]')
                }, "job_offer")
            else:
                offer_content = f"""
                Dear {passport_record.given_names},
                
                We are pleased to offer you the position of {position_details.get('position', '[Position]')} 
                at {self.company_name}.
                
                Position: {position_details.get('position', '[Position]')}
                Department: {position_details.get('department', '[Department]')}
                Salary: {position_details.get('salary', '[Salary]')}
                Start Date: {position_details.get('start_date', '[Start Date]')}
                
                Please confirm your acceptance by replying to this email.
                
                Best regards,
                HR Department
                {self.company_name}
                """
            
            # Send email
            sg = SendGridAPIClient(self.sendgrid_key)
            
            # Try to extract email from phone number field or use provided email
            candidate_email = position_details.get('email', 'candidate@example.com')
            
            message = Mail(
                from_email=Email(self.company_email),
                to_emails=To(candidate_email),
                subject=f"Job Offer - {position_details.get('position', 'Position')} at {self.company_name}",
                html_content=offer_content.replace('\n', '<br>')
            )
            
            response = sg.send(message)
            
            return {
                "success": True, 
                "message": f"Offer letter sent to {candidate_email}",
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to send offer letter: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def process_query_response(self, query_text, context="hr"):
        """Use AI to generate responses to HR queries"""
        if not self.ai.enabled:
            return "AI query processing requires OpenAI API key"
        
        try:
            prompt = f"""
            You are an HR assistant for {self.company_name}. 
            Respond to this query professionally and helpfully:
            
            Query: {query_text}
            Context: {context}
            
            Provide a helpful, professional response that:
            1. Addresses the specific question
            2. Follows standard HR policies and practices
            3. Is friendly but professional
            4. Suggests next steps if applicable
            5. Asks for clarification if needed
            
            Keep the response concise but complete.
            """
            
            response = self.ai.client.chat.completions.create(
                model=self.ai.model,
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return "I apologize, but I'm unable to process your query at the moment. Please contact HR directly."
    
    def evaluate_leave_request(self, employee_data, leave_request):
        """AI-powered leave request evaluation"""
        if not self.ai.enabled:
            return {"recommendation": "manual_review", "reason": "AI not available"}
        
        try:
            prompt = f"""
            Evaluate this leave request and provide a recommendation:
            
            Employee Information:
            - Name: {employee_data.get('name', 'N/A')}
            - Department: {employee_data.get('department', 'N/A')}
            - Position: {employee_data.get('position', 'N/A')}
            - Years of Service: {employee_data.get('years_service', 'N/A')}
            - Previous Leave Balance: {employee_data.get('leave_balance', 'N/A')} days
            - Recent Leave History: {employee_data.get('recent_leaves', 'N/A')}
            
            Leave Request:
            - Type: {leave_request.get('type', 'N/A')}
            - Start Date: {leave_request.get('start_date', 'N/A')}
            - End Date: {leave_request.get('end_date', 'N/A')}
            - Duration: {leave_request.get('duration', 'N/A')} days
            - Reason: {leave_request.get('reason', 'N/A')}
            - Notice Period: {leave_request.get('notice_days', 'N/A')} days advance notice
            
            Consider:
            1. Leave balance availability
            2. Notice period adequacy
            3. Business impact and timing
            4. Leave type appropriateness
            5. Pattern of leave usage
            
            Respond with JSON:
            {{
                "recommendation": "approve" | "reject" | "conditional" | "manual_review",
                "confidence": 0.0-1.0,
                "reasons": ["reason1", "reason2"],
                "conditions": ["condition1"] (if conditional),
                "alternative_dates": "suggestion" (if applicable)
            }}
            """
            
            response = self.ai.client.chat.completions.create(
                model=self.ai.model,
                messages=[
                    {"role": "system", "content": "You are an HR policy assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            return evaluation
            
        except Exception as e:
            logger.error(f"Leave evaluation failed: {str(e)}")
            return {"recommendation": "manual_review", "reason": f"AI evaluation failed: {str(e)}"}
    
    def generate_hr_report(self, report_type, data):
        """Generate various HR reports using AI"""
        if not self.ai.enabled:
            return "HR reports require AI functionality"
        
        try:
            if report_type == "recruitment_summary":
                prompt = f"""
                Generate a recruitment summary report based on this data:
                {json.dumps(data, indent=2)}
                
                Include:
                1. Total applications processed
                2. Passport verification status
                3. Nationality breakdown
                4. Document completeness rates
                5. Processing efficiency metrics
                6. Recommendations for improvement
                """
            
            elif report_type == "leave_analysis":
                prompt = f"""
                Analyze leave patterns and generate insights:
                {json.dumps(data, indent=2)}
                
                Provide:
                1. Leave utilization trends
                2. Department-wise analysis
                3. Seasonal patterns
                4. Policy compliance rates
                5. Recommendations for leave management
                """
            
            else:
                prompt = f"Generate a {report_type} report with this data: {json.dumps(data, indent=2)}"
            
            response = self.ai.client.chat.completions.create(
                model=self.ai.model,
                messages=[
                    {"role": "system", "content": "You are an HR analytics specialist. Generate comprehensive, actionable reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return f"Report generation failed: {str(e)}"
    
    def schedule_follow_up(self, record_id, action_type, days_delay=3):
        """Schedule automated follow-up actions"""
        follow_up_date = datetime.now() + timedelta(days=days_delay)
        
        # This would typically integrate with a task scheduler
        # For now, we'll store in a simple format
        follow_up = {
            "record_id": record_id,
            "action": action_type,
            "scheduled_date": follow_up_date.isoformat(),
            "status": "scheduled"
        }
        
        logger.info(f"Scheduled {action_type} follow-up for record {record_id} on {follow_up_date}")
        return follow_up
    
    def auto_verify_documents(self, passport_record):
        """AI-powered document verification"""
        if not self.ai.enabled:
            return {"verified": False, "reason": "AI verification not available"}
        
        try:
            prompt = f"""
            Verify this passport data for completeness and consistency:
            
            Passport Number: {passport_record.passport_number}
            Name: {passport_record.given_names} {passport_record.surname}
            Nationality: {passport_record.nationality}
            Date of Birth: {passport_record.date_of_birth}
            Issue Date: {passport_record.date_of_issue}
            Expiry Date: {passport_record.date_of_expiry}
            
            Check for:
            1. All required fields present
            2. Date logic (birth < issue < expiry)
            3. Name consistency
            4. Passport number format validity
            5. Expiry date (should be future)
            
            Return JSON:
            {{
                "verified": true/false,
                "confidence": 0.0-1.0,
                "missing_fields": ["field1"],
                "issues": ["issue1"],
                "risk_level": "low" | "medium" | "high"
            }}
            """
            
            response = self.ai.client.chat.completions.create(
                model=self.ai.model,
                messages=[
                    {"role": "system", "content": "You are a document verification specialist. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            verification = json.loads(response.choices[0].message.content)
            return verification
            
        except Exception as e:
            logger.error(f"Document verification failed: {str(e)}")
            return {"verified": False, "reason": f"Verification failed: {str(e)}"}