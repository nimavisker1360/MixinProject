"""
Mixin.ir API Integration Service
Integrates with Persian e-commerce platform to add discovered Turkish products
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from proxy_service import proxy_service
from wireguard_proxy_client import wireguard_client

class MixinAPIService:
    def __init__(self, api_key: str, base_url: str = "https://api.mixin.ir"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Api-Key {api_key}',
            'Content-Type': 'application/json'
        }
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None, timeout: int = 15) -> Dict:
        """Make HTTP request to Mixin API - VPS has direct access"""
        url = f"{self.base_url}/api/management/v1{endpoint}"
        
        try:
            # Direct connection from VPS (no proxy needed)
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method.upper() == 'POST':
                if files:
                    # For multipart/form-data requests (with images)
                    headers = {'Authorization': f'Api-Key {self.api_key}'}
                    response = requests.post(url, headers=headers, files=files, timeout=timeout)
                else:
                    # For JSON requests
                    response = requests.post(url, headers=self.headers, json=data, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Mixin API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response: {e.response.text}")
            raise

    # Category Management
    def get_categories(self, page: int = 1) -> Dict:
        """Get list of categories from Mixin shop"""
        return self._make_request('GET', f'/categories/?page={page}')
    
    def create_category(self, name: str, description: str = "", parent: Optional[int] = None) -> Dict:
        """Create new category in Mixin shop"""
        data = {
            'name': name,
            'description': description,
            'available': True,
            'categories_menu_show': True
        }
        if parent:
            data['parent'] = parent
            
        return self._make_request('POST', '/categories/', data)
    
    def get_category_by_name(self, name: str) -> Optional[Dict]:
        """Find category by name"""
        categories = self.get_categories()
        for category in categories.get('results', []):
            if category['name'] == name:
                return category
        return None
    
    # Brand Management
    def get_brands(self, page: int = 1) -> Dict:
        """Get list of brands from Mixin shop"""
        return self._make_request('GET', f'/brands/?page={page}')
    
    def create_brand(self, name: str) -> Dict:
        """Create new brand in Mixin shop"""
        data = {'name': name}
        return self._make_request('POST', '/brands/', data)
    
    def get_brand_by_name(self, name: str) -> Optional[Dict]:
        """Find brand by name"""
        brands = self.get_brands()
        for brand in brands.get('results', []):
            if brand['name'] == name:
                return brand
        return None
    
    # Product Management
    def get_products(self, page: int = 1) -> Dict:
        """Get list of products from Mixin shop"""
        return self._make_request('GET', f'/products/?page={page}')
    
    def create_product(self, product_data: Dict) -> Dict:
        """Create new product in Mixin shop
        
        Args:
            product_data: Dictionary containing product information
                - name: Product name (required)
                - description: Product description
                - price: Product price
                - category_id: Category ID
                - brand_id: Brand ID
                - available: Boolean (default True)
                - image_url: URL of product image
        """
        return self._make_request('POST', '/products/', product_data)
    
    def add_product_image(self, product_id: int, image_url: str, alt_text: str = "") -> Dict:
        """Add image to product"""
        data = {
            'product': product_id,
            'image_url': image_url,
            'alt_text': alt_text
        }
        return self._make_request('POST', f'/products/{product_id}/images/', data)
    
    # Turkish Product Integration
    def add_turkish_product_to_shop(self, turkish_product: Dict) -> Dict:
        """Add a discovered Turkish product to Mixin shop
        
        Args:
            turkish_product: Product data from SerpAPI + OpenAI processing
                - persian_title: Translated product name
                - title: Original Turkish title
                - price_toman: Price converted to Toman
                - description: Product description (optional)
                - image: Product image URL
                - source: Source website
                - link: Original product link
                - category: Product category
        """
        try:
            # Ensure we have a category
            category_name = turkish_product.get('category', 'محصولات ترکیه')
            category = self.get_category_by_name(category_name)
            if not category:
                # Create category if it doesn't exist
                category_result = self.create_category(
                    name=category_name,
                    description=f"محصولات {category_name} از ترکیه"
                )
                category_id = category_result.get('id')
            else:
                category_id = category['id']
            
            # Create or get brand (using source website as brand)
            brand_name = turkish_product.get('source', 'ترکیه')
            brand = self.get_brand_by_name(brand_name)
            if not brand:
                brand_result = self.create_brand(brand_name)
                brand_id = brand_result.get('id')
            else:
                brand_id = brand['id']
            
            # Prepare product data for Mixin API
            product_data = {
                'name': turkish_product.get('persian_title', turkish_product.get('title', 'محصول ترکیه')),
                'description': f"""
{turkish_product.get('description', '')}

🇹🇷 محصول اصل ترکیه
💰 قیمت: {turkish_product.get('price_toman', 0):,} تومان
🔗 لینک اصلی: {turkish_product.get('link', '')}
📱 منبع: {turkish_product.get('source', '')}

این محصول از فروشگاه‌های معتبر ترکیه تهیه و با کیفیت بالا ارائه می‌شود.
                """.strip(),
                'price': turkish_product.get('price_toman', 0),
                'category': category_id,
                'brand': brand_id,
                'available': True,
                'stock': 10,  # Default stock
                'original_url': turkish_product.get('link', ''),
            }
            
            # Create product
            product_result = self.create_product(product_data)
            product_id = product_result.get('id')
            
            # Add product image if available
            if turkish_product.get('image') and product_id:
                try:
                    self.add_product_image(
                        product_id=product_id,
                        image_url=turkish_product['image'],
                        alt_text=turkish_product.get('persian_title', turkish_product.get('title', ''))
                    )
                except Exception as e:
                    logging.warning(f"Could not add image for product {product_id}: {e}")
            
            logging.info(f"Successfully added Turkish product to Mixin shop: {product_id}")
            return {
                'success': True,
                'product_id': product_id,
                'category_id': category_id,
                'brand_id': brand_id,
                'mixin_url': f"{self.base_url}/product/{product_id}/"
            }
            
        except Exception as e:
            logging.error(f"Failed to add Turkish product to Mixin shop: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def bulk_add_turkish_products(self, products: List[Dict]) -> List[Dict]:
        """Add multiple Turkish products to shop"""
        results = []
        for product in products:
            result = self.add_turkish_product_to_shop(product)
            results.append(result)
        return results
    
    # Order Management
    def get_orders(self, page: int = 1) -> Dict:
        """Get list of orders"""
        return self._make_request('GET', f'/orders/?page={page}')
    
    def get_order_details(self, order_id: int) -> Dict:
        """Get specific order details"""
        return self._make_request('GET', f'/orders/{order_id}/')

# Initialize service with API key
def get_mixin_service(api_key: str) -> MixinAPIService:
    """Factory function to create Mixin API service"""
    return MixinAPIService(api_key)

# Category mapping for Turkish to Persian categories
TURKISH_CATEGORY_MAPPING = {
    'fashion': 'مد و پوشاک',
    'beauty': 'زیبایی و آرایش', 
    'electronics': 'الکترونیک',
    'mobile': 'موبایل و تبلت',
    'home': 'خانه و آشپزخانه',
    'toys': 'اسباب بازی',
    'sports': 'ورزش و سرگرمی',
    'books': 'کتاب و مجله',
    'health': 'سلامت و زیبایی',
    'automotive': 'خودرو و موتورسیکلت'
}

def get_persian_category(english_category: str) -> str:
    """Convert English category to Persian"""
    return TURKISH_CATEGORY_MAPPING.get(english_category.lower(), 'محصولات ترکیه')