#!/bin/bash

# Upsun Deployment Script for TrackFutura
# Linux/macOS version  
# Project: inhoolfrqniuu

echo "🚀 TrackFutura Upsun Deployment Script"
echo "Project: inhoolfrqniuu"
echo "========================================"

# Check if Upsun CLI is installed
echo "🔧 Checking Upsun CLI..."
if ! command -v upsun &> /dev/null; then
    echo "❌ Upsun CLI not found!"
    echo "Please install Upsun CLI first:"
    echo "  curl -f https://cli.upsun.com/installer | sh"
    echo "  Or visit: https://docs.upsun.com/dev-tools/cli/install"
    exit 1
fi
echo "✅ Upsun CLI found"

# Check if logged in
echo "🔐 Checking Upsun authentication..."
if ! upsun auth:info &> /dev/null; then
    echo "❌ Not authenticated with Upsun!"
    echo "Please log in first:"
    echo "  upsun auth:login"
    exit 1
fi
echo "✅ Authenticated with Upsun"

# Set project context
echo "📋 Setting project context..."
PROJECT_ID="inhoolfrqniuu"
if ! upsun project:set-default $PROJECT_ID; then
    echo "❌ Failed to set project context!"
    echo "Available projects:"
    upsun projects
    exit 1
fi
echo "✅ Project context set to $PROJECT_ID"

# Show current project info
echo "📊 Project Information:"
upsun project:info

# Deploy the application
echo "🚀 Starting deployment..."
echo "This will deploy your current Git state to Upsun..."

read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

# Push to Upsun
echo "📤 Pushing to Upsun..."
if ! upsun push --yes; then
    echo "❌ Deployment failed!"
    exit 1
fi

echo "✅ Deployment completed!"
echo ""

# Show deployment URL
echo "🌐 Your application should be available at:"
echo "  https://main-bvxea6i-inhoolfrqniuu.upsun.app"
echo ""

# Environment variables reminder
echo "⚠️  IMPORTANT: Set environment variables in Upsun console:"
echo "1. Go to: https://console.upsun.com/projects/inhoolfrqniuu"
echo "2. Navigate to Environment > Variables"
echo "3. Add these required variables:"
echo "   - APIFY_API_TOKEN (your Apify API token)"
echo "   - OPENAI_API_KEY (your OpenAI API key)"
echo ""

echo "🎉 Deployment complete! Monitor your app in the Upsun console."