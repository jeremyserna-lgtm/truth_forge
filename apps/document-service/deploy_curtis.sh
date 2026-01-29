#!/bin/bash
# Deploy Curtis's portal to Vercel

cd /Users/jeremyserna/truth_forge/apps/document-service

echo "📝 Staging files for Curtis's portal deployment..."

# Add the new files
git add public/curtis.html
git add src/services/userContext.ts
git add src/services/gemini.ts
git add src/api/routes/customer.ts

echo "✅ Files staged:"
git status --short

echo ""
echo "Ready to commit and deploy to truth-forge.ai"
echo ""
echo "Next steps:"
echo "1. Review the changes above"
echo "2. Run: git commit -m 'Add Curtis personalized portal with user context'"
echo "3. Run: git push"
echo "4. Vercel will auto-deploy to https://truth-forge.ai"
echo ""
echo "Then Curtis's page will be live at:"
echo "🍬 https://truth-forge.ai/portal/curtis.html"
