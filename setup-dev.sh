#!/bin/bash

# Track-Futura Development Setup Script
# This script sets up the development environment for new team members

set -e  # Exit on any error

echo "🚀 Setting up Track-Futura Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop first."
    echo "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

print_success "Docker and Docker Compose are installed ✓"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp env.development.template .env
    print_warning "Please review and update the .env file with your specific configuration"
    print_warning "Ask your team lead for the BrightData API key"
else
    print_status ".env file already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p backend/staticfiles
mkdir -p backend/media
mkdir -p logs

# Build development containers
print_status "Building Docker containers (this may take a few minutes)..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.dev.yml build
else
    docker compose -f docker-compose.dev.yml build
fi

print_success "Docker containers built successfully ✓"

# Start the development environment
print_status "Starting development environment..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.dev.yml up -d
else
    docker compose -f docker-compose.dev.yml up -d
fi

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Run database migrations
print_status "Running database migrations..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
else
    docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
fi

# Create superuser (optional)
print_status "Would you like to create a Django superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
    else
        docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
    fi
fi

# Load demo data (optional)
print_status "Would you like to load demo data? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata demo_data.json 2>/dev/null || print_warning "Demo data not found, skipping..."
    else
        docker compose -f docker-compose.dev.yml exec backend python manage.py loaddata demo_data.json 2>/dev/null || print_warning "Demo data not found, skipping..."
    fi
fi

print_success "🎉 Development environment setup complete!"
echo ""
echo "Access your application at:"
echo "  📱 Frontend: http://localhost:3000"
echo "  🔧 Backend API: http://localhost:8000"
echo "  👨‍💼 Django Admin: http://localhost:8000/admin"
echo ""
echo "Useful commands:"
echo "  📊 View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  🛑 Stop services: docker-compose -f docker-compose.dev.yml down"
echo "  🔄 Restart services: docker-compose -f docker-compose.dev.yml restart"
echo "  🧹 Clean up: docker-compose -f docker-compose.dev.yml down -v"
echo ""
echo "For more information, see DEVELOPER_ONBOARDING.md"
