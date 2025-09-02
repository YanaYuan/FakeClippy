#!/usr/bin/env python3
"""
Simple validation script for Vercel deployment readiness
"""
import os
import json
import sys

def check_vercel_readiness():
    print("🔍 Checking Vercel deployment readiness...\n")
    
    issues = []
    warnings = []
    
    # 1. Check if API directory exists
    if not os.path.exists('api'):
        issues.append("❌ 'api' directory not found")
    else:
        print("✅ API directory exists")
    
    # 2. Check if api/index.py exists
    if not os.path.exists('api/index.py'):
        issues.append("❌ 'api/index.py' not found")
    else:
        print("✅ API handler file exists")
        
        # Check if it's using the correct Vercel format
        with open('api/index.py', 'r') as f:
            content = f.read()
            if 'BaseHTTPRequestHandler' in content:
                print("✅ Using correct Vercel serverless format")
            else:
                warnings.append("⚠️  API handler might not be in correct Vercel format")
    
    # 3. Check if static directory exists
    if not os.path.exists('static'):
        issues.append("❌ 'static' directory not found")
    else:
        print("✅ Static directory exists")
    
    # 4. Check if static files exist
    static_files = ['static/index.html', 'static/script.js', 'static/style.css']
    for file in static_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            issues.append(f"❌ {file} not found")
    
    # 5. Check if vercel.json exists
    if not os.path.exists('vercel.json'):
        issues.append("❌ 'vercel.json' not found")
    else:
        print("✅ Vercel configuration exists")
        
        # Validate vercel.json format
        try:
            with open('vercel.json', 'r') as f:
                config = json.load(f)
                if 'builds' in config and 'routes' in config:
                    print("✅ Vercel configuration format is valid")
                else:
                    warnings.append("⚠️  Vercel configuration might be incomplete")
        except json.JSONDecodeError:
            issues.append("❌ vercel.json is not valid JSON")
    
    # 6. Check API dependencies
    if os.path.exists('api/requirements.txt'):
        print("✅ API requirements.txt exists")
        with open('api/requirements.txt', 'r') as f:
            deps = f.read()
            if 'requests' in deps:
                print("✅ Required 'requests' dependency found")
            else:
                warnings.append("⚠️  'requests' dependency might be missing")
    else:
        warnings.append("⚠️  api/requirements.txt not found")
    
    # 7. Check static script.js API configuration
    if os.path.exists('static/script.js'):
        try:
            with open('static/script.js', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'window.location.origin' in content:
                    print("✅ Static script.js uses dynamic API URL")
                else:
                    warnings.append("⚠️  Static script.js might have hardcoded localhost URL")
        except UnicodeDecodeError:
            warnings.append("⚠️  Could not read static/script.js due to encoding issues")
    
    # 8. Check environment configuration
    if os.path.exists('.env.example'):
        print("✅ Environment template exists")
    else:
        warnings.append("⚠️  .env.example not found - users won't know what environment variables to set")
    
    # 9. Check gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content:
                print("✅ .gitignore properly excludes .env files")
            else:
                warnings.append("⚠️  .gitignore might not exclude .env files")
    
    print("\n" + "="*60)
    print("📋 DEPLOYMENT READINESS SUMMARY")
    print("="*60)
    
    if not issues:
        print("🎉 Your project is ready for Vercel deployment!")
        print("\n📝 Deployment checklist:")
        print("   1. Push code to GitHub")
        print("   2. Connect GitHub repo to Vercel")
        print("   3. Add environment variables in Vercel dashboard:")
        print("      - CLAUDE_API_KEY=your_actual_api_key")
        print("      - CLAUDE_BASE_URL=https://www.dmxapi.cn/v1")
        print("      - CLAUDE_MODEL=claude-sonnet-4-20250514")
        print("   4. Deploy!")
    else:
        print("🚨 Issues found that need to be fixed:")
        for issue in issues:
            print(f"   {issue}")
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)} found):")
        for warning in warnings:
            print(f"   {warning}")
    
    print(f"\n📊 Status: {len(issues)} critical issues, {len(warnings)} warnings")
    
    return len(issues) == 0

if __name__ == '__main__':
    success = check_vercel_readiness()
    sys.exit(0 if success else 1)
