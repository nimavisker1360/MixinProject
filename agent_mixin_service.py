"""
Agent Mixin API Service - Persian Shop Integration
Based on the original mixinproject mixin_api_service.py
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

class AgentMixinService:
    """Agent Mixin API service for Persian shop integration"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.mixin.ir"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'AgentChatBot/1.0'
        }
        logging.info(f"🔗 Agent Mixin service initialized: {base_url}")
    
    def test_connection(self) -> bool:
        """Test connection to Mixin API"""
        try:
            response = requests.get(
                f"{self.base_url}/api/test",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info("✅ Agent Mixin API connection successful")
                return True
            else:
                logging.error(f"❌ Agent Mixin API test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Agent Mixin connection test error: {e}")
            return False
    
    def get_categories(self) -> List[Dict]:
        """Get list of categories from Mixin shop"""
        try:
            response = requests.get(
                f"{self.base_url}/api/categories",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('data', [])
                logging.info(f"✅ Retrieved {len(categories)} categories from Mixin")
                return categories
            else:
                logging.error(f"❌ Failed to get categories: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Categories fetch error: {e}")
            return []
    
    def get_brands(self) -> List[Dict]:
        """Get list of brands from Mixin shop"""
        try:
            response = requests.get(
                f"{self.base_url}/api/brands",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                brands = data.get('data', [])
                logging.info(f"✅ Retrieved {len(brands)} brands from Mixin")
                return brands
            else:
                logging.error(f"❌ Failed to get brands: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Brands fetch error: {e}")
            return []
    
    def get_products(self, page: int = 1, limit: int = 20, category_id: Optional[int] = None) -> Dict:
        """Get list of products from Mixin shop"""
        try:
            params = {
                'page': page,
                'limit': limit
            }
            
            if category_id:
                params['category_id'] = category_id
            
            response = requests.get(
                f"{self.base_url}/api/products",
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('data', [])
                total = data.get('total', 0)
                logging.info(f"✅ Retrieved {len(products)} products from Mixin (total: {total})")
                return {
                    'products': products,
                    'total': total,
                    'page': page,
                    'limit': limit
                }
            else:
                logging.error(f"❌ Failed to get products: {response.status_code}")
                return {'products': [], 'total': 0}
                
        except Exception as e:
            logging.error(f"❌ Products fetch error: {e}")
            return {'products': [], 'total': 0}
    
    def upload_product(self, turkish_product: Dict) -> bool:
        """
        Upload a Turkish product to Mixin Persian shop
        
        Args:
            turkish_product: Product data from SerpAPI + OpenAI processing
        
        Returns:
            bool: Success status
        """
        try:
            # Map Turkish product data to Mixin format
            mixin_product = self._map_turkish_to_mixin(turkish_product)
            
            response = requests.post(
                f"{self.base_url}/api/products",
                headers=self.headers,
                json=mixin_product,
                timeout=20
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                product_id = result.get('data', {}).get('id')
                logging.info(f"✅ Product uploaded to Mixin: ID {product_id}")
                return True
            else:
                logging.error(f"❌ Product upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Product upload error: {e}")
            return False
    
    def bulk_upload_products(self, products: List[Dict]) -> Dict:
        """
        Bulk upload multiple products to Mixin
        
        Args:
            products: List of Turkish products
            
        Returns:
            Dict: Upload results summary
        """
        results = {
            'total': len(products),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, product in enumerate(products):
            try:
                logging.info(f"📤 Uploading product {i+1}/{len(products)}: {product.get('title', 'Unknown')}")
                
                success = self.upload_product(product)
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Product {i+1}: Upload failed")
                
                # Add delay between uploads
                if i < len(products) - 1:
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Product {i+1}: {str(e)}")
                logging.error(f"❌ Bulk upload error for product {i+1}: {e}")
        
        logging.info(f"📊 Bulk upload completed: {results['successful']}/{results['total']} successful")
        return results
    
    def _map_turkish_to_mixin(self, turkish_product: Dict) -> Dict:
        """Map Turkish product data to Mixin format"""
        try:
            # Extract basic information
            title = turkish_product.get('persian_title', turkish_product.get('title', ''))
            description = turkish_product.get('persian_description', '')
            price = turkish_product.get('toman_price', 0)
            original_price = turkish_product.get('extracted_price', 0)
            image_url = turkish_product.get('thumbnail', '')
            source_url = turkish_product.get('link', '')
            source = turkish_product.get('source', 'ترکیه')
            
            # Create Mixin product format
            mixin_product = {
                'name': title[:200],  # Limit title length
                'description': description or f"محصول اصل ترکیه - {title}",
                'price': int(price) if price else 0,
                'original_price': float(original_price) if original_price else 0,
                'currency': 'تومان',
                'original_currency': 'TRY',
                'status': 'active',
                'category_id': self._determine_category(title),
                'brand': source,
                'country_origin': 'ترکیه',
                'source_url': source_url,
                'images': [image_url] if image_url else [],
                'tags': self._extract_tags(title),
                'specifications': {
                    'منشا': 'ترکیه',
                    'منبع': source,
                    'قیمت_اصلی': f"{original_price} TRY" if original_price else '',
                    'نرخ_تبدیل': '2950 تومان به ازای هر لیر'
                },
                'meta_data': {
                    'imported_from': 'turkish_shopping_bot',
                    'import_date': self._get_current_timestamp(),
                    'agent_processed': True
                }
            }
            
            return mixin_product
            
        except Exception as e:
            logging.error(f"❌ Product mapping error: {e}")
            return {}
    
    def _determine_category(self, title: str) -> Optional[int]:
        """Determine category based on product title"""
        title_lower = title.lower()
        
        # Category mapping based on keywords
        category_keywords = {
            1: ['لباس', 'پیراهن', 'شلوار', 'کت', 'مانتو', 'dress', 'shirt', 'pants'],
            2: ['آرایش', 'کرم', 'لوازم', 'beauty', 'makeup', 'cosmetic', 'cream'],
            3: ['موبایل', 'گوشی', 'کیس', 'phone', 'mobile', 'case', 'accessory'],
            4: ['اسباب', 'بازی', 'toy', 'game', 'کودک', 'children'],
            5: ['حیوان', 'سگ', 'گربه', 'pet', 'dog', 'cat'],
            6: ['ویتامین', 'سلامت', 'vitamin', 'health', 'supplement']
        }
        
        for category_id, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category_id
        
        return 1  # Default category
    
    def _extract_tags(self, title: str) -> List[str]:
        """Extract tags from product title"""
        title_lower = title.lower()
        tags = []
        
        # Common tags
        tag_keywords = {
            'ترکیه': ['turkish', 'turkey', 'ترکیه'],
            'زنانه': ['women', 'woman', 'زنانه', 'بانوان'],
            'مردانه': ['men', 'man', 'مردانه', 'آقایان'],
            'کودک': ['kid', 'child', 'baby', 'کودک', 'بچه'],
            'ارزان': ['cheap', 'affordable', 'ارزان', 'مقرون'],
            'کیفیت': ['quality', 'premium', 'کیفیت', 'باکیفیت']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                tags.append(tag)
        
        tags.append('محصول_ترکیه')  # Always add this tag
        return tags
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def search_mixin_products(self, query: str, limit: int = 10) -> List[Dict]:
        """Search products in Mixin database"""
        try:
            params = {
                'q': query,
                'limit': limit
            }
            
            response = requests.get(
                f"{self.base_url}/api/products/search",
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('data', [])
                logging.info(f"🔍 Found {len(products)} products in Mixin for: {query}")
                return products
            else:
                logging.error(f"❌ Mixin search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Mixin search error: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by ID"""
        try:
            response = requests.get(
                f"{self.base_url}/api/products/{product_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                product = data.get('data')
                logging.info(f"✅ Retrieved product {product_id} from Mixin")
                return product
            else:
                logging.error(f"❌ Failed to get product {product_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Product fetch error: {e}")
            return None