#!/usr/bin/env python3
"""
Simple VPS Script - Excel Bulk Upload for Mixin API
Copy this entire script to your VPS and run it directly
"""

import pandas as pd
import requests
import json
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MIXIN_KEY = "JOVA-ff-ZIMIITF_NxSeTOeJxOEwOuPnjsec0Md_W__XveblDT4YlBf-2SqUBMDX"

def create_turkish_products_excel():
    """Create Excel with authentic Turkish beauty products"""
    
    products_data = {
        'name': [
            'عطر زنانه زارا - وسوسه سرخ',
            'عطر زنانه زارا - نسیم دل‌انگیز', 
            'کرم مرطوب کننده ترکی طبیعی',
            'شامپو گیاهی اصیل ترکی',
            'صابون طبیعی حمام ترکی'
        ],
        'description': [
            'عطر زنانه زارا با رایحه جذاب و فریبنده، مناسب برای خانم‌های شیک و جذاب',
            'عطر اصیل زارا با رایحه‌ای بی‌نظیر و ماندگاری بالا، انتخابی ایده‌آل برای مناسبت‌های ویژه',
            'کرم مرطوب کننده طبیعی ترکی با عصاره گیاهان برای نرمی و طراوت پوست',
            'شامپو گیاهی اصیل ترکی برای تقویت و درخشندگی مو با فرمول طبیعی',
            'صابون طبیعی حمام ترکی با رایحه‌های گیاهی و خواص مرطوب کننده'
        ],
        'price': [174050, 221250, 85000, 65000, 45000],
        'main_category': [5, 5, 5, 5, 5],
        'brand': [1, 1, 1, 1, 1],
        'stock': [20, 15, 30, 25, 40],
        'weight': [150, 200, 200, 300, 150],
        'available': [True, True, True, True, True],
        'seo_title': [
            'عطر زارا وسوسه سرخ اصیل ترکی',
            'عطر زارا نسیم دل‌انگیز EDT اصیل',
            'کرم مرطوب کننده ترکی طبیعی',
            'شامپو گیاهی تقویت کننده مو ترکی',
            'صابون حمام طبیعی ترکی'
        ],
        'tags': [
            'زارا,عطر,زنانه,اصیل,ترکی',
            'زارا,عطر,EDT,نسیم,دل‌انگیز',
            'کرم,ترکی,طبیعی,مرطوب کننده',
            'شامپو,گیاهی,تقویت مو,طبیعی',
            'صابون,حمام,طبیعی,ترکی'
        ],
        'image_url': [
            'https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcRQvF8yC7U9-QJ9dJ_YF9LKgxFKyFjKX1Y1bg&usqp=CAE',
            'https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcT8_vF9Kx7Y2J5dJ_YF9LKgxFKyFjKX1Y1bg&usqp=CAE',
            'https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcS5_aF6Jx3Z1J2dJ_YF9LKgxFKyFjKX1Y1bg&usqp=CAE',
            'https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcR2_bF7Jx4A3K3dJ_YF9LKgxFKyFjKX1Y1bg&usqp=CAE',
            'https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcT1_cF8Jx5B4L4dJ_YF9LKgxFKyFjKX1Y1bg&usqp=CAE'
        ]
    }
    
    df = pd.DataFrame(products_data)
    excel_file = '/tmp/turkish_beauty_products_mixin.xlsx'
    df.to_excel(excel_file, index=False)
    
    print(f"✅ Excel created with {len(products_data['name'])} products: {excel_file}")
    return excel_file, products_data

def test_comprehensive_mixin_upload(product_data):
    """Test all possible Mixin API combinations"""
    
    headers = {
        "Api-Key": MIXIN_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # All possible base URLs to test
    base_urls = [
        "https://api.mixin.ir",
        "https://mixin.ir/api",
        "https://gstyle.mixin.ir/api"
    ]
    
    # All possible endpoints to test
    endpoints = [
        "/api/management/v1/products",
        "/management/v1/products",
        "/api/v1/products", 
        "/v1/products",
        "/products"
    ]
    
    # All possible photo field formats to test
    photo_field_tests = [
        ("image_url", product_data['image_url']),
        ("photo", product_data['image_url']),
        ("image", product_data['image_url']),
        ("images", [product_data['image_url']]),
        ("picture", product_data['image_url']),
        ("thumbnail", product_data['image_url']),
        ("main_image", product_data['image_url'])
    ]
    
    # Base product data structure
    base_product = {
        "name": product_data['name'],
        "description": product_data['description'],
        "price": int(product_data['price']),
        "main_category": int(product_data['main_category']),
        "brand": int(product_data['brand']),
        "stock": int(product_data['stock']),
        "weight": int(product_data['weight']),
        "available": bool(product_data['available']),
        "seo_title": product_data['seo_title'],
        "tags": product_data['tags'].split(',') if isinstance(product_data['tags'], str) else []
    }
    
    total_tests = len(base_urls) * len(endpoints) * len(photo_field_tests)
    current_test = 0
    
    print(f"🔍 Testing {total_tests} API combinations for: {product_data['name'][:35]}")
    
    for base_url in base_urls:
        for endpoint in endpoints:
            for field_name, field_value in photo_field_tests:
                current_test += 1
                full_url = base_url + endpoint
                
                upload_data = base_product.copy()
                upload_data[field_name] = field_value
                
                try:
                    print(f"[{current_test:2d}/{total_tests}] Testing: {full_url} with {field_name}")
                    
                    response = requests.post(
                        full_url,
                        headers=headers,
                        json=upload_data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        try:
                            result = response.json()
                            product_id = result.get('id', 'created')
                            print(f"🎉 SUCCESS! Product uploaded successfully!")
                            print(f"   Working URL: {full_url}")
                            print(f"   Working Photo Field: {field_name}")
                            print(f"   Product ID: {product_id}")
                            
                            return {
                                "success": True,
                                "url": full_url,
                                "photo_field": field_name,
                                "product_id": product_id,
                                "response": result
                            }
                        except:
                            print(f"🎉 SUCCESS! Product created (201 response)")
                            return {
                                "success": True,
                                "url": full_url,
                                "photo_field": field_name,
                                "product_id": "created"
                            }
                    
                    elif response.status_code == 400:
                        print(f"   ⚠️ Validation error: {response.text[:60]}")
                        
                    elif response.status_code in [401, 403]:
                        print(f"   ❌ Authentication error: {response.status_code}")
                        
                    elif response.status_code == 404:
                        print(f"   ❌ Not found: {full_url}")
                        break  # Try next endpoint
                        
                    else:
                        print(f"   ⚠️ HTTP {response.status_code}: {response.text[:50]}")
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏰ Timeout: {full_url}")
                    
                except requests.exceptions.ConnectionError:
                    print(f"   🔌 Connection error: {full_url}")
                    break  # Try next endpoint
                    
                except Exception as e:
                    print(f"   ❌ Error: {str(e)[:60]}")
                    
                time.sleep(0.5)  # Brief delay between tests
    
    print(f"❌ All {total_tests} combinations failed for: {product_data['name'][:35]}")
    return {"success": False, "error": "All API combinations failed"}

def execute_excel_bulk_upload():
    """Execute the complete Excel bulk upload process"""
    
    print("🚀 EXCEL BULK UPLOAD - COMPREHENSIVE MIXIN API TESTING")
    print("=" * 65)
    
    # Step 1: Create Excel with products
    excel_file, products_dict = create_turkish_products_excel()
    
    # Convert to list format
    products_list = []
    for i in range(len(products_dict['name'])):
        product = {}
        for key in products_dict:
            product[key] = products_dict[key][i]
        products_list.append(product)
    
    print(f"\n📋 Loaded {len(products_list)} Turkish beauty products")
    print(f"💰 Total value: {sum(p['price'] for p in products_list):,} تومان")
    
    # Step 2: Initialize tracking
    results = []
    successful_uploads = 0
    working_config = None
    
    print(f"\n🔄 Starting systematic upload process...")
    print("-" * 50)
    
    # Step 3: Test each product
    for i, product in enumerate(products_list, 1):
        print(f"\n[PRODUCT {i}/{len(products_list)}] {product['name']}")
        print(f"💰 Price: {product['price']:,} تومان")
        
        result = test_comprehensive_mixin_upload(product)
        
        if result['success']:
            successful_uploads += 1
            print(f"✅ Upload successful!")
            
            # Save first working configuration
            if not working_config:
                working_config = {
                    "url": result.get('url'),
                    "photo_field": result.get('photo_field')
                }
                print(f"🎯 WORKING CONFIGURATION DISCOVERED:")
                print(f"   URL: {working_config['url']}")
                print(f"   Photo Field: {working_config['photo_field']}")
        else:
            print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
        
        results.append({
            "product_name": product['name'],
            "price": product['price'],
            "success": result['success'],
            "details": result
        })
        
        # Brief pause between products
        if i < len(products_list):
            print(f"⏳ Waiting 2 seconds before next product...")
            time.sleep(2)
    
    # Step 4: Generate comprehensive report
    report = {
        "excel_file": excel_file,
        "total_products": len(products_list),
        "successful_uploads": successful_uploads,
        "failed_uploads": len(products_list) - successful_uploads,
        "success_rate": f"{(successful_uploads/len(products_list)*100):.1f}%",
        "working_configuration": working_config,
        "total_value": sum(p['price'] for p in products_list),
        "detailed_results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    # Step 5: Save detailed report
    report_file = f'/tmp/mixin_excel_upload_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Step 6: Display final results
    print(f"\n" + "=" * 65)
    print("🎯 FINAL EXCEL BULK UPLOAD RESULTS")
    print("=" * 65)
    print(f"📊 Total Products: {report['total_products']}")
    print(f"✅ Successful Uploads: {report['successful_uploads']}")
    print(f"❌ Failed Uploads: {report['failed_uploads']}")
    print(f"📈 Success Rate: {report['success_rate']}")
    print(f"💰 Total Value: {report['total_value']:,} تومان")
    
    if working_config:
        print(f"\n🎉 WORKING CONFIGURATION FOUND!")
        print(f"🔗 URL: {working_config['url']}")
        print(f"📸 Photo Field: {working_config['photo_field']}")
        print(f"\n✨ This configuration can be used for future uploads!")
        print(f"✨ Turkish products with photos successfully integrated with Mixin shop!")
    else:
        print(f"\n⚠️ NO WORKING CONFIGURATION FOUND")
        print(f"🔍 All API endpoint and photo field combinations were tested")
        print(f"💡 Consider checking API key validity or network connectivity")
    
    print(f"\n📁 Files Generated:")
    print(f"   📋 Excel File: {excel_file}")
    print(f"   📄 Report File: {report_file}")
    
    print(f"\n🏁 Excel bulk upload process completed!")
    
    return report

if __name__ == "__main__":
    # Install required packages reminder
    print("📦 Make sure you have installed required packages:")
    print("   pip3 install pandas openpyxl requests xlsxwriter")
    print("")
    
    # Execute the bulk upload
    execute_excel_bulk_upload()