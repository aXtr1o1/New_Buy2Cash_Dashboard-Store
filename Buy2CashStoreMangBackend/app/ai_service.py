import os
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from openai import OpenAI
from app.ai_prompts import *

logger = logging.getLogger(__name__)

class StoreManagerAI:
    """AI assistant using GPT model with dynamic query capabilities"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.openai_key:
            try:
                self.client = OpenAI(api_key=self.openai_key)
                logger.info("AI assistant ready with GPT-4o mini")
            except Exception as e:
                logger.warning(f"AI setup failed: {str(e)}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured")
    
    def is_available(self) -> bool:
        """Check if AI is ready"""
        return self.client is not None
    
    def generate_mongodb_filter(self, user_question: str) -> Dict[str, Any]:
        """Generate MongoDB filter from natural language question"""
        if not self.is_available():
            return {"status": "APPROVED", "stage": "ACTIVATE"}
        
        try:
            prompt = MONGODB_QUERY_GENERATOR_PROMPT.format(user_question=user_question)
            
            response = self.client.chat.completions.create(
                model=MINI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_ROLES["mongodb_expert"]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1  
            )
            
            filter_json = response.choices.message.content.strip()
            if filter_json.startswith("```"):
                filter_json = filter_json.split("\n")[1:-1]
                filter_json = "\n".join(filter_json)
            
            mongo_filter = json.loads(filter_json)
            logger.info(f"Generated MongoDB filter for '{user_question}': {mongo_filter}")
            
            return mongo_filter
            
        except Exception as e:
            logger.exception(f"Failed to generate MongoDB filter: {str(e)}")
            return {"status": "APPROVED", "stage": "ACTIVATE"}
    
    def get_dynamic_nlp_response(self, user_query: str, store_id: str, products: List[Dict], categories: List[Dict]) -> str:
        """Generate dynamic NLP response based on actual data"""
        if not self.is_available():
            return self._dynamic_simple_response(user_query, products, categories)
        
        try:
            products_count = len(products)
            categories_count = len(categories)

            sample_products = [p.get('ProductName', 'Unknown') for p in products[:5]]
            sample_categories = [c.get('name', 'Unknown') for c in categories[:5]]
            
            sample_data = {
                "sample_products": sample_products,
                "sample_categories": sample_categories
            }

            prompt = NLP_QUERY_PROMPT.format(
                query=user_query,
                store_id=store_id,
                products_count=products_count,
                categories_count=categories_count,
                sample_data=json.dumps(sample_data)
            )
            
            response = self.client.chat.completions.create(
                model=MINI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": STORE_ASSISTANT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices.message.content.strip()
            
        except Exception as e:
            logger.exception("Dynamic AI response failed")
            return self._dynamic_simple_response(user_query, products, categories)
    
    def _dynamic_simple_response(self, user_query: str, products: List[Dict], categories: List[Dict]) -> str:
        """Enhanced fallback response with actual data"""
        query_lower = user_query.lower()

        if any(word in query_lower for word in ["categories", "category", "types"]) and categories:
            category_names = [c.get('name', 'Unknown') for c in categories[:10]]
            return RESPONSE_TEMPLATES["categories_from_products"].format(
                categories=", ".join(category_names)
            )

        elif products:
            product_names = [p.get('ProductName', 'Unknown') for p in products[:5]]
            return RESPONSE_TEMPLATES["products_found"].format(
                count=len(products),
                query=user_query,
                products=", ".join(product_names)
            )

        elif categories:
            category_names = [c.get('name', 'Unknown') for c in categories[:5]]
            return RESPONSE_TEMPLATES["categories_found"].format(
                count=len(categories),
                query=user_query,
                categories=", ".join(category_names)
            )

        else:
            return RESPONSE_TEMPLATES["no_results"].format(query=user_query)

    def suggest_substitutes(self, product_data: Dict, similar_products: List[Dict], top_n: int = 5) -> List[Dict]:
        """Suggest product alternatives using GPT"""
        if not self.is_available() or not similar_products:
            return self._simple_substitutes(product_data, similar_products, top_n)
        
        try:
            product_info = f"Product: {product_data.get('ProductName', 'Unknown')}, Price: ₹{product_data.get('offerPrice', 0)}"
            
            alternatives = []
            for prod in similar_products[:10]:
                alternatives.append({
                    "name": prod.get("ProductName", "Unknown"),
                    "price": prod.get("offerPrice", 0),
                    "category": prod.get("category", "Unknown"),
                    "id": str(prod.get("_id", ""))
                })
            
            user_prompt = SUBSTITUTION_USER_PROMPT.format(
                top_n=top_n,
                product_info=product_info,
                alternatives=json.dumps(alternatives, indent=2)
            )
            
            response = self.client.chat.completions.create(
                model=MINI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": SUBSTITUTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            ai_response=response.choices[0].message.content

            
            try:
                substitutes = json.loads(ai_response)
                if isinstance(substitutes, list):
                    return substitutes[:top_n]
            except:
                pass
            
            return self._simple_substitutes(product_data, similar_products, top_n)
            
        except Exception as e:
            logger.exception("AI substitutes failed")
            return self._simple_substitutes(product_data, similar_products, top_n)
    
    def recommend_discounts(self, performance: Dict, unsold_products: List[Dict]) -> Dict:
        """Recommend discounts using GPT"""
        if not self.is_available():
            return self._simple_discount_advice(performance, unsold_products)
        
        try:
            performance_summary = {
                "completion_rate": performance.get("performance_metrics", {}).get("completion_rate", 0),
                "total_orders": performance.get("performance_metrics", {}).get("total_orders", 0),
                "revenue": performance.get("performance_metrics", {}).get("total_revenue", 0)
            }
            
            old_products_count = len([p for p in unsold_products[:10] if p.get("days_in_inventory", 0) > 30])
            
            user_prompt = DISCOUNT_USER_PROMPT.format(
                performance_summary=json.dumps(performance_summary),
                old_products_count=old_products_count
            )
            
            response = self.client.chat.completions.create(
                model=MINI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": DISCOUNT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.4
            )
            
            ai_response = response.choices.message.content.strip()
            
            try:
                recommendations = json.loads(ai_response)
                return recommendations
            except:
                pass
            
            return self._simple_discount_advice(performance, unsold_products)
            
        except Exception as e:
            logger.exception("AI discount advice failed")
            return self._simple_discount_advice(performance, unsold_products)
    
    def _simple_substitutes(self, product_data: Dict, similar_products: List[Dict], top_n: int) -> List[Dict]:
        """Simple substitutes without AI"""
        substitutes = []
        original_price = product_data.get("offerPrice", 0)
        
        for i, product in enumerate(similar_products[:top_n]):
            price = product.get("offerPrice", 0)
            substitutes.append({
                "product_id": str(product.get("_id", "")),
                "product_name": product.get("ProductName", "Unknown Product"),
                "similarity_score": round(0.8 - (i * 0.1), 2),
                "price_difference": round(price - original_price, 2),
                "reason": "Similar product in same category"
            })
        
        return substitutes
    
    def _simple_discount_advice(self, performance: Dict, unsold_products: List[Dict]) -> Dict:
        """Simple discount advice without AI"""
        old_count = len([p for p in unsold_products if p.get("days_in_inventory", 0) > 30])
        
        return {
            "strategy": "Clear old inventory with targeted discounts while maintaining margins",
            "quick_actions": [
                f"Apply 20-30% discount to {old_count} products over 30 days old",
                "Create bundle deals with popular items",
                "Run limited-time promotions"
            ],
            "discount_suggestions": [
                {"category": "30+ days old", "discount": "20-30%", "reason": "Clear aging inventory"},
                {"category": "slow movers", "discount": "10-15%", "reason": "Improve cash flow"},
                {"category": "popular items", "discount": "5-10%", "reason": "Drive traffic"}
            ]
        }

# Global AI assistant
ai_assistant = StoreManagerAI()
