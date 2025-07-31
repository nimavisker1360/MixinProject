from app import app, db
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from google_auth import google_auth
from models import User, Favorite, CartItem, Order, OrderItem
from product_service import product_service
import uuid
import logging
import os
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import JONE MADARET bot functionality
from complete_bot import TurkishShoppingBot

# Initialize the bot
bot = TurkishShoppingBot()
logging.info("🤖 Telegram bot initialized for webhook handling")

# Register blueprints
app.register_blueprint(google_auth, url_prefix='/')

# JONE MADARET TELEGRAM WEBHOOK - UNIFIED WORKING VERSION
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """JONE MADARET Telegram webhook - unified working functionality"""
    try:
        update = request.get_json()
        if not update:
            return "OK", 200
        
        logging.info(f"📥 Webhook received update: {update.get('update_id', 'unknown')}")
        
        # Process message or callback query
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            logging.info(f"📝 Message from {chat_id}: {text}")
            
            if text == '/start':
                bot.send_welcome_message(chat_id)
            elif text and len(text) > 0:
                # Handle text search with photo delivery
                bot._handle_text_search(chat_id, text)
        
        elif 'callback_query' in update:
            # Handle navigation button clicks
            callback_query = update['callback_query']
            chat_id = callback_query['message']['chat']['id']
            callback_data = callback_query['data']
            
            logging.info(f"🔘 Button clicked: {callback_data} by user {chat_id}")
            
            # Handle main category navigation
            if callback_data == 'fashion_categories':
                bot.send_fashion_categories(chat_id)
            elif callback_data == 'beauty_categories':
                bot.send_beauty_categories(chat_id)
            elif callback_data == 'mobile_pc_categories':
                bot.send_mobile_pc_categories(chat_id)
            elif callback_data == 'toys_gadgets_categories':
                bot.send_toys_gadgets_categories(chat_id)
            elif callback_data == 'pet_categories':
                bot.send_pet_categories(chat_id)
            elif callback_data == 'vitamins_categories':
                bot.send_vitamins_categories(chat_id)
            
            # Handle subcategory searches
            elif callback_data.startswith('fashion_search:'):
                query = callback_data.replace('fashion_search:', '')
                bot._handle_category_search(chat_id, query, '👗')
            elif callback_data.startswith('beauty_search:'):
                query = callback_data.replace('beauty_search:', '')
                bot._handle_category_search(chat_id, query, '💄')
            elif callback_data.startswith('mobile_search:'):
                query = callback_data.replace('mobile_search:', '')
                bot._handle_category_search(chat_id, query, '📱')
            elif callback_data.startswith('toys_search:'):
                query = callback_data.replace('toys_search:', '')
                bot._handle_category_search(chat_id, query, '🧸')
            elif callback_data.startswith('pet_search:'):
                query = callback_data.replace('pet_search:', '')
                bot._handle_category_search(chat_id, query, '🐾')
            elif callback_data.startswith('vitamins_search:'):
                query = callback_data.replace('vitamins_search:', '')
                bot._handle_category_search(chat_id, query, '💊')
            
            # Handle navigation
            elif callback_data == 'search_guide':
                bot._show_search_guide(chat_id)
            elif callback_data == 'rules':
                bot._show_rules_regulations(chat_id)
            elif callback_data == 'back_to_main':
                bot.send_welcome_message(chat_id)
            elif callback_data.startswith('more_products:'):
                query = callback_data.replace('more_products:', '')
                bot._handle_more_products(chat_id, query)
            
            # Answer callback query
            try:
                requests.post(
                    f"https://api.telegram.org/bot{bot.telegram_token}/answerCallbackQuery",
                    data={'callback_query_id': callback_query['id']},
                    timeout=5
                )
            except Exception as e:
                logging.error(f"Failed to answer callback query: {e}")
        
        return "OK", 200
        
    except Exception as e:
        logging.error(f"❌ Webhook error: {e}")
        return "OK", 200

# Test webhook endpoint
@app.route('/webhook_test', methods=['GET'])
def webhook_test():
    """Test endpoint to verify webhook is working"""
    return jsonify({
        'status': 'Webhook endpoint is working',
        'bot_initialized': bool(bot),
        'methods': ['POST for webhook', 'GET for test']
    })

# Bot status endpoint
@app.route('/bot_status')
def bot_status():
    """Check bot status"""
    try:
        # Test SerpAPI connectivity
        test_products = bot.search_authentic_products_serpapi("test", 1)
        serpapi_working = len(test_products) > 0
        
        return jsonify({
            'bot_initialized': True,
            'serpapi_working': serpapi_working,
            'openai_configured': bool(bot.openai_key),
            'telegram_configured': bool(bot.telegram_token),
            'webhook_url': 'https://milestone-tracker-eminemkh.replit.app/webhook'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'bot_initialized': False})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    
    if not query:
        flash('لطفا کلمه کلیدی برای جستجو وارد کنید', 'error')
        return redirect(url_for('index'))
    
    # Translate Persian query to Turkish if needed
    turkish_query = product_service.translate_query(query)
    
    # Check if user wants to add products to Mixin shop
    add_to_shop = request.args.get('add_to_shop', 'false').lower() == 'true'
    
    if add_to_shop:
        # Search and automatically add to Mixin shop
        result = product_service.search_and_add_to_shop(turkish_query, category, per_page)
        products = result.get('products', [])
        
        # Add success message if products were added to shop
        if result.get('mixin_products_added', 0) > 0:
            flash(f"{result['mixin_products_added']} محصول به فروشگاه شما اضافه شد!", 'success')
    else:
        # Regular search
        products = product_service.search_products(turkish_query, category, per_page)
    
    # Calculate pagination (simple approach)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return render_template('search.html', 
                         products=products, 
                         query=query,
                         category=category,
                         page=page,
                         has_more=len(products) >= per_page,
                         mixin_service_available=bool(product_service.mixin_service))

@app.route('/category/<name>')
def category(name):
    page = int(request.args.get('page', 1))
    per_page = 20
    
    # Get products by category
    products = product_service.search_by_category(name, per_page)
    
    # Category names mapping
    category_names = {
        'fashion': 'مد و پوشاک',
        'beauty': 'زیبایی و آرایش',
        'electronics': 'الکترونیک و موبایل',
        'toys': 'اسباب‌بازی و گجت',
        'pets': 'حیوانات خانگی',
        'health': 'سلامت و ویتامین'
    }
    
    category_title = category_names.get(name, name.title())
    
    return render_template('category.html', 
                         products=products,
                         category_name=name,
                         category_title=category_title,
                         page=page,
                         has_more=len(products) >= per_page)

@app.route('/favorites')
@login_required
def favorites():
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.added_at.desc()).all()
    return render_template('favorites.html', favorites=user_favorites)

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).order_by(CartItem.added_at.desc()).all()
    
    # Calculate total
    total = sum(item.product_price * item.quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

# API Routes for AJAX functionality

@app.route('/api/add-to-favorites', methods=['POST'])
@login_required
def add_to_favorites():
    data = request.get_json()
    
    try:
        favorite = Favorite(
            user_id=current_user.id,
            product_title=data['title'],
            product_price=data['price'],
            product_image=data.get('image', ''),
            product_link=data['link'],
            product_source=data.get('source', '')
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'محصول به علاقه‌مندی‌ها اضافه شد'})
        
    except Exception as e:
        db.session.rollback()
        if 'unique_user_favorite' in str(e):
            return jsonify({'success': False, 'message': 'این محصول قبلا به علاقه‌مندی‌ها اضافه شده'})
        return jsonify({'success': False, 'message': 'خطا در اضافه کردن به علاقه‌مندی‌ها'})

@app.route('/api/add-to-mixin-shop', methods=['POST'])
def add_to_mixin_shop():
    """Add a single product to Mixin shop"""
    data = request.get_json()
    
    if not product_service.mixin_service:
        return jsonify({'success': False, 'message': 'سرویس فروشگاه در دسترس نیست'})
    
    try:
        # Prepare product data for Mixin
        turkish_product = {
            'persian_title': data.get('persian_title', data.get('title')),
            'title': data.get('title'),
            'price_toman': data.get('price_toman', 0),
            'description': data.get('description', ''),
            'image': data.get('image', ''),
            'source': data.get('source', ''),
            'link': data.get('link', ''),
            'category': data.get('category', 'محصولات ترکیه')
        }
        
        # Add to Mixin shop
        result = product_service.mixin_service.add_turkish_product_to_shop(turkish_product)
        
        if result.get('success'):
            return jsonify({
                'success': True, 
                'message': 'محصول به فروشگاه شما اضافه شد!',
                'product_id': result.get('product_id'),
                'mixin_url': result.get('mixin_url')
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'خطا در اضافه کردن: {result.get("error", "خطای نامشخص")}'
            })
            
    except Exception as e:
        logging.error(f"Error adding product to Mixin shop: {e}")
        return jsonify({'success': False, 'message': 'خطا در اضافه کردن محصول به فروشگاه'})

@app.route('/mixin-status')
def mixin_status():
    """Show Mixin API connection status with VPN info"""
    api_key = product_service.mixin_api_key if product_service.mixin_api_key else None
    
    # Test connectivity
    connectivity_info = {
        'direct_failed': True,
        'proxy_failed': True,
        'demo_active': bool(product_service.mixin_service),
        'filtering_detected': True,  # Based on our tests
        'replit_url': request.host,
        'error_type': 'Country-based network filtering',
        'wireguard_ready': True
    }
    
    return render_template('mixin_status.html', 
                         api_key=api_key, 
                         connectivity=connectivity_info)

@app.route('/setup-wireguard', methods=['GET', 'POST'])
def setup_wireguard():
    """Setup WireGuard VPN configuration"""
    if request.method == 'GET':
        return render_template('wireguard_setup.html')
    
    # Handle POST request with config
    config_content = request.form.get('config')
    if not config_content:
        return jsonify({'success': False, 'message': 'No configuration provided'})
    
    try:
        from wireguard_proxy_client import test_with_config
        
        # Test WireGuard config with Mixin API
        api_key = product_service.mixin_api_key or 'rvw9_vlTqzUsXV1rN7wIYW7z1B0v5b2pPK0JWdYMwUekDZ8Ewj3rJ4lLZWGYjD8r'
        result = test_with_config(config_content, api_key)
        
        if result.get('overall_success'):
            return jsonify({
                'success': True, 
                'message': 'WireGuard setup successful and Mixin API accessible!',
                'details': result
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Setup incomplete: {result.get("error", "Unknown error")}',
                'details': result
            })
            
    except Exception as e:
        logging.error(f"WireGuard setup error: {e}")
        return jsonify({'success': False, 'message': f'Setup failed: {e}'})

@app.route('/api/bulk-add-to-mixin-shop', methods=['POST'])
def bulk_add_to_mixin_shop():
    """Add multiple products to Mixin shop"""
    data = request.get_json()
    products = data.get('products', [])
    category = data.get('category')
    
    if not product_service.mixin_service:
        return jsonify({'success': False, 'message': 'سرویس فروشگاه در دسترس نیست'})
    
    if not products:
        return jsonify({'success': False, 'message': 'هیچ محصولی برای اضافه کردن یافت نشد'})
    
    try:
        results = product_service.add_products_to_mixin_shop(products, category)
        successful = [r for r in results if r.get('success')]
        
        return jsonify({
            'success': True,
            'message': f'{len(successful)} از {len(products)} محصول به فروشگاه اضافه شد',
            'added_count': len(successful),
            'total_count': len(products),
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Error bulk adding products to Mixin shop: {e}")
        return jsonify({'success': False, 'message': 'خطا در اضافه کردن محصولات به فروشگاه'})

@app.route('/api/test-mixin-connectivity')
def test_mixin_connectivity():
    """Test Mixin API connectivity through current setup"""
    try:
        from wireguard_proxy_client import SimplifiedWireGuardClient
        
        api_key = product_service.mixin_api_key or 'rvw9_vlTqzUsXV1rN7wIYW7z1B0v5b2pPK0JWdYMwUekDZ8Ewj3rJ4lLZWGYjD8r'
        
        # Test with current client (may include proxy if configured)
        client = SimplifiedWireGuardClient()
        result = client.test_mixin_api(api_key)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error testing Mixin connectivity: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'categories_found': 0,
            'response_time': None
        })

@app.route('/api/remove-from-favorites', methods=['POST'])
@login_required
def remove_from_favorites():
    data = request.get_json()
    
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        product_link=data['link']
    ).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'success': True, 'message': 'محصول از علاقه‌مندی‌ها حذف شد'})
    
    return jsonify({'success': False, 'message': 'محصول یافت نشد'})

@app.route('/api/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    
    try:
        # Check if item already exists in cart
        existing_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_link=data['link']
        ).first()
        
        if existing_item:
            existing_item.quantity += data.get('quantity', 1)
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_title=data['title'],
                product_price=data['price'],
                product_image=data.get('image', ''),
                product_link=data['link'],
                product_source=data.get('source', ''),
                quantity=data.get('quantity', 1)
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'محصول به سبد خرید اضافه شد'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'خطا در اضافه کردن به سبد خرید'})

@app.route('/api/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_link=data['link']
    ).first()
    
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'محصول از سبد خرید حذف شد'})
    
    return jsonify({'success': False, 'message': 'محصول یافت نشد'})

@app.route('/api/update-cart-quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    data = request.get_json()
    
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_link=data['link']
    ).first()
    
    if cart_item:
        cart_item.quantity = max(1, data['quantity'])
        db.session.commit()
        return jsonify({'success': True, 'message': 'تعداد محصول به‌روزرسانی شد'})
    
    return jsonify({'success': False, 'message': 'محصول یافت نشد'})

@app.route('/api/counters')
def counters():
    """Get cart and favorites counters for navbar"""
    if current_user.is_authenticated:
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        favorites_count = Favorite.query.filter_by(user_id=current_user.id).count()
    else:
        cart_count = 0
        favorites_count = 0
    
    return jsonify({
        'cart_count': cart_count,
        'favorites_count': favorites_count
    })

@app.route('/api/recent-favorites')
@login_required
def recent_favorites():
    """Get recent favorites for homepage"""
    favorites = Favorite.query.filter_by(user_id=current_user.id)\
                             .order_by(Favorite.added_at.desc())\
                             .limit(3).all()
    
    return jsonify({
        'favorites': [{
            'title': f.product_title,
            'price': f.product_price,
            'image': f.product_image,
            'link': f.product_link
        } for f in favorites]
    })

@app.route('/api/cart-preview')
@login_required
def cart_preview():
    """Get cart preview for homepage"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id)\
                              .order_by(CartItem.added_at.desc())\
                              .limit(3).all()
    
    total = sum(item.product_price * item.quantity for item in cart_items)
    
    return jsonify({
        'items': [{
            'title': item.product_title,
            'price': item.product_price,
            'quantity': item.quantity,
            'image': item.product_image,
            'link': item.product_link
        } for item in cart_items],
        'total': total
    })

@app.route('/api/create-order', methods=['POST'])
@login_required
def create_order():
    """Create order from cart items"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'سبد خرید خالی است'})
    
    try:
        # Calculate total
        total = sum(item.product_price * item.quantity for item in cart_items)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            order_number=f"GS{uuid.uuid4().hex[:8].upper()}",
            total_amount=total
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_title=cart_item.product_title,
                product_price=cart_item.product_price,
                product_image=cart_item.product_image,
                product_link=cart_item.product_link,
                quantity=cart_item.quantity
            )
            db.session.add(order_item)
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'سفارش با موفقیت ثبت شد',
            'order_number': order.order_number
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'خطا در ثبت سفارش'})

# Static files for PWA
@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

# Import webapp routes to complete the setup
from webapp_route import setup_webapp_routes
app = setup_webapp_routes(app)

# Debug: Print all registered routes
logging.info("🔍 Registered Flask routes:")
for rule in app.url_map.iter_rules():
    logging.info(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")

if __name__ == '__main__':
    logging.info("🚀 Starting Flask app with both PWA and Telegram webhook")
    app.run(host='0.0.0.0', port=5000, debug=True)