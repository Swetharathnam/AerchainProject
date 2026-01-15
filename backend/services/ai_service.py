from google import genai
from google.genai import types
import json
import asyncio

from typing import Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if settings.GOOGLE_API_KEY:
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        else:
            self.client = None

    async def extract_rfp_structure(self, natural_language_input: str) -> Dict[str, Any]:
        """
        Extracts structured RFP data from natural language text using Gemini.
        Returns a JSON object with title, description, budget, requirements, etc.
        """
        if not settings.GOOGLE_API_KEY:
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
        
        retry_count = 3
        
        for attempt in range(retry_count):
            try:
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ]
                
                def generate_content():
                    response_text = ""
                    for chunk in self.client.models.generate_content_stream(
                        model='gemini-2.5-flash-lite',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            response_mime_type='application/json'
                        )
                    ):
                        if hasattr(chunk, 'text') and chunk.text:
                            response_text += chunk.text
                    return response_text

                loop = asyncio.get_event_loop()
                raw_text = await loop.run_in_executor(None, generate_content)
                logger.info(f"AI response (attempt {attempt+1}): {raw_text[:100]}...")
                
                # Extract JSON from the text
                json_start = raw_text.find('{')
                json_end = raw_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    clean_json_text = raw_text[json_start:json_end]
                else:
                    clean_json_text = raw_text.strip()
                
                return json.loads(clean_json_text)

            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Rate limit hit. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"AI Extraction Error: {error_str}")
                    title_fallback = (natural_language_input[:40] + "...") if len(natural_language_input) > 40 else natural_language_input
                    return {
                        "title": f"[AI Error] {title_fallback}",
                        "description": f"AI extraction failed: {error_str}\n\nOriginal Text: {natural_language_input}",
                        "budget": None,
                        "currency": "USD",
                        "error": error_str
                    }

    async def analyze_proposal(self, rfp_context: str, proposal_text: str) -> Dict[str, Any]:
        """
        Analyzes a vendor proposal against the RFP context.
        Returns JSON with score, rationale, extracted specific values.
        """
        if not settings.GOOGLE_API_KEY:
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
        
        retry_count = 3
        
        for attempt in range(retry_count):
            try:
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ]
                
                def generate_content():
                    response_text = ""
                    for chunk in self.client.models.generate_content_stream(
                        model='gemini-2.5-flash-lite',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            response_mime_type='application/json'
                        )
                    ):
                        if hasattr(chunk, 'text') and chunk.text:
                            response_text += chunk.text
                    return response_text

                loop = asyncio.get_event_loop()
                raw_text = await loop.run_in_executor(None, generate_content)
                logger.info(f"Proposal Analysis response (attempt {attempt+1}): {raw_text[:100]}...")
                
                # Extract JSON from the text
                json_start = raw_text.find('{')
                json_end = raw_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    clean_json_text = raw_text[json_start:json_end]
                else:
                    clean_json_text = raw_text.strip()
                
                return json.loads(clean_json_text)

            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Rate limit hit in analysis. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"AI Analysis Error: {error_str}")
                    return {
                        "score": 0,
                        "rationale": f"Analysis failed: {error_str}",
                        "extracted_price": 0,
                        "pros": [],
                        "cons": [],
                        "error": error_str
                    }



    async def compare_proposals(self, rfp_context: str, proposals_list: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compares multiple vendor proposals against the RFP.
        Returns a comparative analysis and recommendation.
        """
        if not settings.GOOGLE_API_KEY:
            return {
                "recommendation": "AI Key missing. Demo mode.",
                "comparison_matrix": [],
                "best_vendor_id": None
            }
            
        proposals_text = ""
        for p in proposals_list:
            proposals_text += f"\n--- VENDOR {p.get('vendor_name', 'Unknown')} (ID: {p.get('vendor_id')}) ---\n{p.get('proposal_text')}\n"

        prompt = f"""
        You are a procurement manager. Compare the following Vendor Proposals for the given RFP.
        
        RFP REQUIREMENTS:
        {rfp_context}
        
        VENDOR PROPOSALS:
        {proposals_text}
        
        Return ONLY a raw JSON object with:
        - recommendation: A summary text explaining the best choice.
        - best_vendor_id: The ID of the best vendor (integer).
        - comparison_matrix: A list of objects, one for each vendor, containing:
            - vendor_name: Name of vendor.
            - score: 0-100 score.
            - key_strengths: String summary of strengths.
            - key_weaknesses: String summary of weaknesses.
            - price_ranking: "Lowest", "Medium", "Highest" (if price is mentioned).
        
        JSON:
        """
        
        retry_count = 3
        
        for attempt in range(retry_count):
            try:
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ]
                
                def generate_content():
                    response_text = ""
                    for chunk in self.client.models.generate_content_stream(
                        model='gemini-2.5-flash-lite',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            response_mime_type='application/json'
                        )
                    ):
                        if hasattr(chunk, 'text') and chunk.text:
                            response_text += chunk.text
                    return response_text

                loop = asyncio.get_event_loop()
                raw_text = await loop.run_in_executor(None, generate_content)
                logger.info(f"Comparison response (attempt {attempt+1}): {raw_text[:100]}...")
                
                # Extract JSON from the text
                json_start = raw_text.find('{')
                json_end = raw_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    clean_json_text = raw_text[json_start:json_end]
                else:
                    clean_json_text = raw_text.strip()
                
                return json.loads(clean_json_text)

            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Rate limit hit in comparison. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"AI Comparison Error: {error_str}")
                    return {
                        "recommendation": f"Comparison failed: {error_str}",
                        "comparison_matrix": [],
                        "best_vendor_id": None
                    }

ai_service = AIService()


