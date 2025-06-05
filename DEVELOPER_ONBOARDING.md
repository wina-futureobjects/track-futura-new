# 🚀 Track-Futura Developer Onboarding Guide

Welcome to the Track-Futura development team! This guide will get you up and running quickly with our Docker-based development environment.

## 📋 Prerequisites

Before you start, make sure you have the following installed:

### Required Software

1. **Docker Desktop** (Latest version)
   - 📥 Download: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - ✅ Ensure you have at least 4GB RAM allocated to Docker
   - ✅ Enable WSL2 integration (Windows users)

2. **Git** (Latest version)
   - 📥 Download: [git-scm.com](https://git-scm.com/)

3. **Code Editor** (Recommended: VS Code)
   - 📥 Download: [code.visualstudio.com](https://code.visualstudio.com/)
   - 🔌 Install recommended extensions (see section below)

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 10GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux

## 🛠️ Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Track-Futura
   ```

2. **Run the setup script:**
   ```bash
   # On macOS/Linux:
   ./setup-dev.sh

   # On Windows (Git Bash or WSL):
   bash setup-dev.sh

   # On Windows (PowerShell):
   # Follow manual setup below
   ```

3. **Access the application:**
   - 📱 Frontend: [http://localhost:3000](http://localhost:3000)
   - 🔧 Backend API: [http://localhost:8000](http://localhost:8000)
   - 👨‍💼 Django Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

### Option 2: Manual Setup

1. **Clone and navigate:**
   ```bash
   git clone <repository-url>
   cd Track-Futura
   ```

2. **Create environment file:**
   ```bash
   cp env.development.template .env
   ```

3. **Update environment variables** (ask team lead for API keys):
   ```bash
   # Edit .env file with your preferred editor
   # Update BRIGHTDATA_API_KEY with the actual key
   ```

4. **Build and start containers:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d --build
   ```

5. **Run database migrations:**
   ```bash
   docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
   ```

## 🏗️ Project Architecture

### Directory Structure
```
Track-Futura/
├── backend/                 # Django REST API
│   ├── config/             # Django settings
│   ├── users/              # User management
│   ├── reports/            # Report generation
│   ├── analytics/          # Analytics features
│   ├── data_collector/     # Data collection utilities
│   ├── instagram_data/     # Instagram scraping
│   ├── facebook_data/      # Facebook scraping
│   ├── linkedin_data/      # LinkedIn scraping
│   ├── tiktok_data/        # TikTok scraping
│   ├── brightdata_integration/ # BrightData API
│   └── chat/              # Real-time chat
├── frontend/               # React TypeScript app
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page-level components
│   │   ├── services/       # API service functions
│   │   └── utils/          # Utility functions
│   └── public/
├── docker-compose.yml      # Production configuration
├── docker-compose.dev.yml  # Development configuration
└── DEVELOPER_ONBOARDING.md # This file
```

### Technology Stack

**Backend:**
- 🐍 Python 3.11 + Django 5.2
- 🔌 Django REST Framework
- 🗄️ SQLite (dev) / PostgreSQL (prod)
- 🚀 Redis for caching
- 📊 Pandas for data processing

**Frontend:**
- ⚛️ React 18 + TypeScript
- 🎨 Material-UI (MUI) + Tailwind CSS
- 📈 Chart.js + Recharts for visualizations
- 🔄 Vite for development
- 🌐 Nginx for serving (production)

## 🔧 Development Workflow

### Daily Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Stop services
docker-compose -f docker-compose.dev.yml down

# Restart services
docker-compose -f docker-compose.dev.yml restart

# Rebuild containers (after dependency changes)
docker-compose -f docker-compose.dev.yml up -d --build

# Clean up everything
docker-compose -f docker-compose.dev.yml down -v
```

### Backend Development

```bash
# Access Django shell
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell

# Run migrations
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Create migrations
docker-compose -f docker-compose.dev.yml exec backend python manage.py makemigrations

# Run tests
docker-compose -f docker-compose.dev.yml exec backend python manage.py test

# Install new Python package
docker-compose -f docker-compose.dev.yml exec backend pip install package-name
# Then update requirements.txt and rebuild

# Access container bash
docker-compose -f docker-compose.dev.yml exec backend bash
```

### Frontend Development

```bash
# Install new npm package
docker-compose -f docker-compose.dev.yml exec frontend npm install package-name

# Run tests
docker-compose -f docker-compose.dev.yml exec frontend npm test

# Access container shell
docker-compose -f docker-compose.dev.yml exec frontend sh

# Build production bundle
docker-compose -f docker-compose.dev.yml exec frontend npm run build
```

## 🔐 Login Credentials

### Demo User Account
- **Username:** `demo`
- **Password:** `demo123`
- **Email:** `demo@trackfutura.com`
- **Role:** Regular User

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** (empty)
- **Role:** Administrator

### Creating/Resetting Demo Credentials

If you need to create or reset the demo user credentials:

```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py create_demo_user
```

This command will:
- Create a demo user if it doesn't exist
- Reset the demo user password to `demo123`
- Reset the admin user password to `admin123`
- Ensure proper user profiles and roles are created

### Testing Login

Test the login functionality:

```bash
# Test demo user
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Test admin user
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Both should return a 200 status with authentication token and user details.

⚠️ **Security Note:** These are development credentials only! Never use in production.

## 📝 Code Standards

### Python/Django

- **PEP 8** style guide compliance
- **Type hints** for function parameters and returns
- **Docstrings** for all classes and functions
- **Django best practices**: Use ViewSets, proper serializers
- **API design**: RESTful endpoints with consistent naming

```python
# Example: Good Django ViewSet
class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing social media reports.

    Provides CRUD operations for reports with filtering and export capabilities.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs) -> Response:
        """Create a new report with validation."""
        # Implementation here
        pass
```

### TypeScript/React

- **Strict TypeScript**: No `any` types, proper interfaces
- **Functional components** with hooks
- **Material-UI** design patterns
- **Proper error handling** and loading states

```typescript
// Example: Good React component
interface ReportProps {
  reportId: string;
  onUpdate: (report: Report) => void;
}

const ReportComponent: React.FC<ReportProps> = ({ reportId, onUpdate }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Implementation here

  return (
    <Card>
      {/* Component JSX */}
    </Card>
  );
};
```

## 🔗 VS Code Extensions (Recommended)

Install these extensions for the best development experience:

### Essential Extensions

1. **Python** (`ms-python.python`)
2. **Django** (`batisteo.vscode-django`)
3. **TypeScript Importer** (`pmneo.tsimporter`)
4. **ES7+ React/Redux/React-Native snippets** (`dsznajder.es7-react-js-snippets`)
5. **Prettier - Code formatter** (`esbenp.prettier-vscode`)
6. **ESLint** (`dbaeumer.vscode-eslint`)
7. **Docker** (`ms-azuretools.vscode-docker`)
8. **GitLens** (`eamodio.gitlens`)

### Optional but Helpful

9. **Material Icon Theme** (`pkief.material-icon-theme`)
10. **Auto Rename Tag** (`formulahendry.auto-rename-tag`)
11. **Bracket Pair Colorizer** (built into VS Code now)
12. **Thunder Client** (`rangav.vscode-thunder-client`) - API testing

### VS Code Settings

Create `.vscode/settings.json` in your project:

```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "emmet.includeLanguages": {
    "typescript": "typescriptreact"
  }
}
```

## 🐛 Debugging

### Backend Debugging

1. **Django Debug Toolbar** (already configured in dev):
   - View SQL queries, performance metrics
   - Access at any API endpoint with `?debug=1`

2. **Container debugging**:
   ```bash
   # View detailed logs
   docker-compose -f docker-compose.dev.yml logs --tail=100 backend

   # Access Python debugger
   docker-compose -f docker-compose.dev.yml exec backend python manage.py shell
   ```

3. **Database inspection**:
   ```bash
   # Access SQLite (development)
   docker-compose -f docker-compose.dev.yml exec backend python manage.py dbshell
   ```

### Frontend Debugging

1. **React Developer Tools** browser extension
2. **Redux DevTools** (if using Redux)
3. **Network tab** for API calls
4. **Console logs** in development:
   ```typescript
   console.log('Debug info:', data);
   ```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
docker-compose -f docker-compose.dev.yml exec backend python manage.py test

# Run specific app tests
docker-compose -f docker-compose.dev.yml exec backend python manage.py test users

# Run with coverage
docker-compose -f docker-compose.dev.yml exec backend coverage run --source='.' manage.py test
docker-compose -f docker-compose.dev.yml exec backend coverage report
```

### Frontend Tests

```bash
# Run tests
docker-compose -f docker-compose.dev.yml exec frontend npm test

# Run tests with coverage
docker-compose -f docker-compose.dev.yml exec frontend npm run test:coverage
```

## 🌐 Environment Variables

### Development Environment

Copy `env.development.template` to `.env` and update:

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `1` |
| `SECRET_KEY` | Django secret key | `dev-secret-key` |
| `BRIGHTDATA_API_KEY` | BrightData API key | Ask team lead |
| `REACT_APP_API_URL` | Frontend API URL | `http://localhost:8000/api` |

### Getting API Keys

**BrightData API Key:**
1. Ask your team lead for the development API key
2. Never commit API keys to git
3. Use environment variables only

## 🔄 Git Workflow

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `refactor/description` - Code refactoring

### Commit Message Format

```
type(scope): description

Examples:
feat(backend): add Instagram data export functionality
fix(frontend): resolve chart rendering issue
docs(readme): update setup instructions
```

### Workflow Steps

1. **Create feature branch:**
   ```bash
   git checkout -b feature/instagram-analytics
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat(analytics): add Instagram engagement metrics"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/instagram-analytics
   ```

4. **Create Pull Request** with:
   - Clear description
   - Screenshots (for UI changes)
   - Testing notes

## 🚨 Common Issues & Solutions

### Docker Issues

**Port already in use:**
```bash
# Find what's using the port
netstat -tulpn | grep :8000

# Kill the process or change port in docker-compose.dev.yml
```

**Container won't start:**
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs backend

# Rebuild container
docker-compose -f docker-compose.dev.yml up -d --build backend
```

**Database issues:**
```bash
# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
```

### Python/Django Issues

**Module not found:**
```bash
# Rebuild backend container
docker-compose -f docker-compose.dev.yml build backend
```

**Migration conflicts:**
```bash
# Access backend container
docker-compose -f docker-compose.dev.yml exec backend bash
python manage.py showmigrations
python manage.py migrate --fake-initial
```

### Frontend Issues

**Node modules issues:**
```bash
# Clear node modules and reinstall
docker-compose -f docker-compose.dev.yml exec frontend rm -rf node_modules
docker-compose -f docker-compose.dev.yml exec frontend npm install
```

**Build errors:**
```bash
# Check TypeScript errors
docker-compose -f docker-compose.dev.yml exec frontend npm run type-check
```

## 📞 Getting Help

### Team Communication

1. **Slack channels:**
   - `#track-futura-dev` - Development discussions
   - `#track-futura-general` - General project updates

2. **Code reviews:**
   - All PRs require at least one review
   - Tag relevant team members

3. **Daily standups:**
   - Share what you're working on
   - Mention any blockers

### Resources

- **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com/)
- **React Documentation**: [react.dev](https://react.dev/)
- **Material-UI**: [mui.com](https://mui.com/)
- **Docker Documentation**: [docs.docker.com](https://docs.docker.com/)

### Who to Contact

- **Technical Lead**: For architecture decisions
- **DevOps Lead**: For deployment and infrastructure
- **Product Manager**: For feature requirements
- **Team Lead**: For API keys and access

## 🎯 Next Steps

After completing setup:

1. **Read the codebase** - Start with `backend/config/` and `frontend/src/`
2. **Pick up a starter issue** - Look for "good first issue" labels
3. **Set up your IDE** - Install recommended extensions
4. **Join team meetings** - Standups, sprint planning
5. **Review existing PRs** - Learn from team code style

## 📚 Additional Documentation

- **API Documentation**: See backend README for endpoint details
- **Component Library**: Check frontend/src/components/
- **Database Schema**: Review Django models in each app
- **Deployment Guide**: See DOCKER_README.md for production setup

---

🎉 **Welcome to the team!** If you have any questions, don't hesitate to ask in Slack or reach out to your team lead.
