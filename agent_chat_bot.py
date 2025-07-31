#!/usr/bin/env python3
"""
Agent Chat Bot - Enhanced Turkish Shopping Assistant
Based on the mixinproject repository structure
"""

import os
import logging
import requests
import json
import time
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

class AgentChatBot:
    def __init__(self):
        """Initialize the Agent Chat Bot with all necessary services"""
        self.telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.serpapi_key = os.environ.get('SERPAPI_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.openai_key)
            logging.info("✅ OpenAI client initialized")
        except Exception as e:
            logging.error(f"❌ OpenAI initialization failed: {e}")
            self.openai_client = None
        
        # Initialize Mixin API service for Persian shop integration
        try:
            from agent_mixin_service import AgentMixinService
            mixin_api_key = os.environ.get('MIXIN_API_KEY', "rvw9_vlTqzUsXV1rN7wIYW7z1B0v5b2pPK0JWdYMwUekDZ8Ewj3rJ4lLZWGYjD8r")
            self.mixin_service = AgentMixinService(mixin_api_key, "https://api.mixin.ir")
            logging.info("✅ Agent Mixin.ir integration configured")
        except Exception as e:
            logging.error(f"⚠️ Agent Mixin service initialization failed: {e}")
            self.mixin_service = None
        
        logging.info("🚀 AGENT CHAT BOT INITIALIZED")
    
    def send_telegram_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> bool:
        """Send a message to Telegram chat"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logging.info(f"✅ Message sent to {chat_id}")
                    return True
            
            logging.error(f"❌ Failed to send message: {response.text}")
            return False
            
        except Exception as e:
            logging.error(f"❌ Telegram message error: {e}")
            return False
    
    def send_welcome_message(self, chat_id: int):
        """Send welcome message with agent capabilities"""
        welcome_text = """🤖 **سلام! به ربات هوشمند خرید ترکیه خوش آمدید**

🎯 **قابلیت‌های من:**
• جستجوی محصولات ترکیه‌ای با ترجمه فارسی
• تشخیص تصاویر و محصولات
• پردازش پیام‌های صوتی
• ادغام با فروشگاه‌های فارسی

💡 **راهنمای استفاده:**
- هر متنی بنویسید تا محصولات مرتبط ترکیه‌ای پیدا کنم
- عکس محصول بفرستید تا موارد مشابه جستجو کنم
- پیام صوتی بفرستید تا تشخیص دهم

🛍️ **دسته‌بندی‌ها:**"""

        # Add category buttons
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "👗 لباس زنانه", "callback_data": "category_women"},
                    {"text": "👔 لباس مردانه", "callback_data": "category_men"}
                ],
                [
                    {"text": "💄 آرایشی", "callback_data": "category_beauty"},
                    {"text": "📱 موبایل", "callback_data": "category_mobile"}
                ],
                [
                    {"text": "🧸 اسباب بازی", "callback_data": "category_toys"},
                    {"text": "🐕 حیوانات", "callback_data": "category_pets"}
                ],
                [
                    {"text": "💊 ویتامین", "callback_data": "category_vitamins"},
                    {"text": "🔍 جستجوی آزاد", "callback_data": "search_free"}
                ]
            ]
        }
        
        self.send_telegram_message(chat_id, welcome_text, keyboard)
    
    def handle_text_message(self, chat_id: int, text: str):
        """Handle text messages with intelligent product search"""
        try:
            logging.info(f"🔍 Processing text search: {text}")
            
            # Send loading message
            loading_msg = "🔍 در حال جستجو در فروشگاه‌های ترکیه..."
            self.send_telegram_message(chat_id, loading_msg)
            
            # Search for products
            products = self.search_turkish_products(text)
            
            if products:
                # Send products to user
                for product in products[:5]:  # Limit to top 5 results
                    self.send_product_message(chat_id, product)
                
                # Send summary message
                summary = f"✅ {len(products)} محصول ترکیه‌ای پیدا شد برای: *{text}*"
                self.send_telegram_message(chat_id, summary)
            else:
                # No products found
                no_result_msg = f"❌ متأسفانه محصولی برای *{text}* یافت نشد.\n\n💡 لطفاً کلمات کلیدی دیگری امتحان کنید."
                self.send_telegram_message(chat_id, no_result_msg)
                
        except Exception as e:
            logging.error(f"❌ Text handling error: {e}")
            error_msg = "❌ خطایی در پردازش پیام رخ داد. لطفاً دوباره تلاش کنید."
            self.send_telegram_message(chat_id, error_msg)
    
    def search_turkish_products(self, query: str) -> List[Dict]:
        """Search for Turkish products using SerpAPI"""
        try:
            # Translate query to English/Turkish if needed
            english_query = self.translate_to_english(query)
            
            # Search using SerpAPI
            search_url = "https://serpapi.com/search"
            params = {
                'engine': 'google_shopping',
                'q': english_query + ' site:trendyol.com OR site:hepsiburada.com',
                'api_key': self.serpapi_key,
                'num': 10,
                'gl': 'tr',  # Turkey
                'hl': 'tr'   # Turkish language
            }
            
            response = requests.get(search_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                shopping_results = data.get('shopping_results', [])
                
                # Process and enhance results
                enhanced_products = []
                for result in shopping_results:
                    enhanced_product = self.enhance_product_data(result, query)
                    enhanced_products.append(enhanced_product)
                
                return enhanced_products
            
            logging.error(f"SerpAPI error: {response.status_code}")
            return []
            
        except Exception as e:
            logging.error(f"❌ Product search error: {e}")
            return []
    
    def translate_to_english(self, persian_text: str) -> str:
        """Translate Persian text to English using OpenAI"""
        try:
            if not self.openai_client:
                return persian_text
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Translate the following Persian text to English for product search. Return only the translation."
                    },
                    {
                        "role": "user",
                        "content": persian_text
                    }
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return persian_text
    
    def enhance_product_data(self, product: Dict, original_query: str) -> Dict:
        """Enhance product data with Persian translation and pricing"""
        try:
            enhanced = product.copy()
            
            # Convert price to Toman
            if 'extracted_price' in product:
                try_price = float(product['extracted_price'])
                toman_price = int(try_price * 2950)  # TRY to Toman conversion
                enhanced['toman_price'] = toman_price
            
            # Translate title to Persian
            if self.openai_client and 'title' in product:
                persian_title = self.translate_to_persian(product['title'])
                enhanced['persian_title'] = persian_title
            
            return enhanced
            
        except Exception as e:
            logging.error(f"Enhancement error: {e}")
            return product
    
    def translate_to_persian(self, english_text: str) -> str:
        """Translate English text to Persian using OpenAI"""
        try:
            if not self.openai_client:
                return english_text
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Translate the following English product title to Persian. Return only the Persian translation."
                    },
                    {
                        "role": "user",
                        "content": english_text
                    }
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Persian translation error: {e}")
            return english_text
    
    def send_product_message(self, chat_id: int, product: Dict):
        """Send a product message with details and buttons"""
        try:
            # Prepare product message
            title = product.get('persian_title', product.get('title', 'محصول'))
            price = product.get('toman_price', 0)
            source = product.get('source', 'فروشگاه ترکیه')
            link = product.get('link', '#')
            
            message_text = f"""🛍️ **{title}**

💰 قیمت: {price:,} تومان
🏪 فروشگاه: {source}
🔗 لینک: [مشاهده محصول]({link})

📞 *برای سفارش با پشتیبانی تماس بگیرید*"""

            # Add action buttons
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🔗 مشاهده محصول", "url": link},
                        {"text": "📞 پشتیبانی", "callback_data": f"support_{product.get('title', '')[:20]}"}
                    ]
                ]
            }
            
            # Send with image if available
            if 'thumbnail' in product:
                self.send_photo_message(chat_id, product['thumbnail'], message_text, keyboard)
            else:
                self.send_telegram_message(chat_id, message_text, keyboard)
                
        except Exception as e:
            logging.error(f"Product message error: {e}")
    
    def send_photo_message(self, chat_id: int, photo_url: str, caption: str, reply_markup: Optional[Dict] = None):
        """Send a photo message with caption"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendPhoto"
            data = {
                'chat_id': chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            response = requests.post(url, data=data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logging.info(f"✅ Photo sent to {chat_id}")
                    return True
            
            logging.error(f"❌ Failed to send photo: {response.text}")
            return False
            
        except Exception as e:
            logging.error(f"❌ Photo message error: {e}")
            return False
    
    def handle_callback_query(self, callback_query: Dict):
        """Handle button callback queries"""
        try:
            chat_id = callback_query['message']['chat']['id']
            data = callback_query['data']
            
            logging.info(f"🔘 Callback received: {data}")
            
            # Handle category searches
            if data.startswith('category_'):
                category = data.replace('category_', '')
                category_queries = {
                    'women': 'لباس زنانه',
                    'men': 'لباس مردانه',
                    'beauty': 'لوازم آرایشی',
                    'mobile': 'لوازم موبایل',
                    'toys': 'اسباب بازی',
                    'pets': 'لوازم حیوانات',
                    'vitamins': 'ویتامین'
                }
                
                if category in category_queries:
                    self.handle_text_message(chat_id, category_queries[category])
            
            # Handle support requests
            elif data.startswith('support_'):
                support_msg = """📞 **پشتیبانی خرید ترکیه**

🔸 تلگرام: @GStyleSupport
🔸 واتساپ: +90 555 123 4567
🔸 ایمیل: support@gstyle.com

⏰ ساعات کاری: 9 صبح تا 9 شب (به وقت ترکیه)"""
                
                self.send_telegram_message(chat_id, support_msg)
            
            # Answer callback query
            answer_url = f"https://api.telegram.org/bot{self.telegram_token}/answerCallbackQuery"
            requests.post(answer_url, data={'callback_query_id': callback_query['id']})
            
        except Exception as e:
            logging.error(f"❌ Callback handling error: {e}")