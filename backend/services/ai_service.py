from google import genai
import os
import json
from typing import Dict, Any

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class AIService:
    def __init__(self):
        if GOOGLE_API_KEY:
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
        else:
            self.client = None

    async def extract_rfp_structure(self, natural_language_input: str) -> Dict[str, Any]:
        """
        Extracts structured RFP data from natural language text using Gemini.
        Returns a JSON object with title, description, budget, requirements, etc.
        """
        if not GOOGLE_API_KEY:
            # Fallback for dev if no key provided
            return {
                "title": "Sample RFP (AI Disabled)",
                "description": natural_language_input,
                "budget": 0,
                "currency": "USD",
                "requirements": []
            }

        prompt = f"""
        You are an expert procurement assistant. 
        Extract a structured Request for Proposal (RFP) from the following user input:
        "{natural_language_input}"
        
        Return ONLY a raw JSON object (no markdown formatting) with the following keys:
        - title: A short, professional title for the RFP.
        - description: A professional summary of the requirements.
        - budget: Numeric value (null if not mentioned).
        - currency: Currency code (default USD).
        - requirements: A list of specific items/requirements (e.g. quantity, specs).
        
        Example JSON:
        {{
            "title": "Laptop Procurement",
            "description": "Purchase of high-performance laptops for engineering team.",
            "budget": 50000,
            "currency": "USD",
            "requirements": ["20x MacBook Pro", "32GB RAM"]
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            # Cleanup potential markdown ticks if Gemini adds them
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"AI Error: {e}")
            # Fallback on error
            return {
                "title": "New RFP",
                "description": natural_language_input,
                "error": "Failed to generate structure"
            }

    async def analyze_proposal(self, rfp_context: str, proposal_text: str) -> Dict[str, Any]:
        """
        Analyzes a vendor proposal against the RFP context.
        Returns JSON with score, rationale, extracted specific values.
        """
        if not GOOGLE_API_KEY:
            return {
                "score": 50,
                "rationale": "AI Key missing. Demo mode.",
                "extracted_price": 0,
                "pros": [],
                "cons": []
            }
            
        prompt = f"""
        You are a procurement expert. Evaluate the following Vendor Proposal against the RFP Requirements.
        
        RFP REQUIREMENTS:
        {rfp_context}
        
        VENDOR PROPOSAL:
        {proposal_text}
        
        Return ONLY a raw JSON object with:
        - score: Integer (0-100) based on how well it meets requirements.
        - rationale: A brief explanation of the score.
        - extracted_price: Numeric value found in proposal (or 0).
        - extracted_timeline: Delivery time mentioned (e.g. "2 weeks").
        - pros: List of strings (strengths).
        - cons: List of strings (weaknesses).
        
        JSON:
        """
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"AI Error: {e}")
            return {
                "score": 0,
                "rationale": f"Analysis failed: {str(e)}",
                "extracted_price": 0,
                "pros": [],
                "cons": []
            }


ai_service = AIService()
