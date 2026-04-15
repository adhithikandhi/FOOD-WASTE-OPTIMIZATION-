#!/usr/bin/env python3
"""
Vercel Deployment Verification Script
Tests the application configurations and readiness for deployment
"""

import os
import json
import sys

def verify_files():
    """Verify all required files exist"""
    required_files = [
        'app.py',
        'api/index.py',
        'vercel.json',
        'requirements.txt',
        'runtime.txt',
        'wsgi.py',
        'templates/index.html',
        'static/style.css',
    ]
    
    print("🔍 Checking required files...")
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def verify_config():
    """Verify configuration files"""
    print("\n🔧 Checking configuration...")
    
    # Check vercel.json
    try:
        with open('vercel.json', 'r') as f:
            vercel_config = json.load(f)
            print("  ✅ vercel.json is valid JSON")
            
            if vercel_config.get('version') == 2:
                print("  ✅ Vercel v2 configuration")
            else:
                print("  ⚠️  Warning: Unexpected Vercel version")
                
            routes = vercel_config.get('routes', [])
            if routes and routes[0].get('dest') == 'api/index.py':
                print("  ✅ Routes configured correctly")
            else:
                print("  ❌ Routes not properly configured")
                return False
    except Exception as e:
        print(f"  ❌ Error reading vercel.json: {e}")
        return False
    
    # Check requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            if 'Flask' in requirements:
                print("  ✅ Flask in requirements.txt")
            if 'Werkzeug' in requirements:
                print("  ✅ Werkzeug in requirements.txt")
            if 'Jinja2' in requirements:
                print("  ✅ Jinja2 in requirements.txt")
    except Exception as e:
        print(f"  ❌ Error reading requirements.txt: {e}")
        return False
    
    return True

def verify_app_structure():
    """Verify Flask app structure"""
    print("\n📁 Checking Flask app structure...")
    
    try:
        # Import the app
        from app import app
        
        # Check if app is Flask instance
        if hasattr(app, 'route'):
            print("  ✅ Flask app created successfully")
        
        # Check routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        print(f"  ✅ Found {len(routes)} routes")
        
        important_routes = ['/', '/health', '/donor_register', '/donor_login']
        for route in important_routes:
            if route in routes:
                print(f"    ✅ {route}")
            else:
                print(f"    ⚠️  {route} not found")
        
        # Check static folder
        if hasattr(app, 'static_folder'):
            print(f"  ✅ Static folder configured: {app.static_folder}")
        
        # Check template folder
        if hasattr(app, 'template_folder'):
            print(f"  ✅ Template folder configured: {app.template_folder}")
        
        return True
    except ImportError as e:
        print(f"  ❌ Cannot import app: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error checking app structure: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 50)
    print("🚀 VERCEL DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    checks = [
        ("Files", verify_files()),
        ("Configuration", verify_config()),
        ("App Structure", verify_app_structure()),
    ]
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✅ All checks passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Push code to GitHub")
        print("2. Go to https://vercel.com")
        print("3. Import your repository")
        print("4. Deploy!\n")
        return 0
    else:
        print("\n❌ Some checks failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
