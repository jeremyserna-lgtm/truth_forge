#!/bin/bash
# Quick setup script for environment variables

echo "🔧 Setting up environment variables for Truth Forge document service..."
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file exists"
else
    echo "❌ .env file not found - creating from template..."
    exit 1
fi

echo ""
echo "📋 Environment Variable Checklist:"
echo ""

# Check each required variable
check_var() {
    local var_name=$1
    local value=$(grep "^${var_name}=" .env | cut -d '=' -f 2-)
    
    if [ -z "$value" ] || [ "$value" = "your_gemini_api_key_here" ]; then
        echo "❌ $var_name - NOT SET"
        return 1
    else
        echo "✅ $var_name - SET"
        return 0
    fi
}

check_var "GEMINI_API_KEY"
check_var "BIGQUERY_PROJECT"
check_var "BIGQUERY_DATASET"
check_var "GOOGLE_APPLICATION_CREDENTIALS"

echo ""
echo "🔗 To get your Gemini API key:"
echo "   Visit: https://aistudio.google.com/app/apikey"
echo ""
echo "📝 After getting your key, edit .env and replace:"
echo "   GEMINI_API_KEY=your_gemini_api_key_here"
echo "with:"
echo "   GEMINI_API_KEY=<your-actual-key>"
echo ""
echo "Then run this script again to verify setup!"
