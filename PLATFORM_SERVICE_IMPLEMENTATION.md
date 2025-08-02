# Platform and Service Management Implementation

## Overview

This document outlines the implementation of a comprehensive platform and service management system for Track-Futura, allowing superadmins to configure available platforms and services, while regular users can only access enabled platform-service combinations.

## Business Rules Implemented

### 1. Platform Management Rules
- **BR-001**: A platform is a social media platform (e.g., Instagram, Facebook, LinkedIn, TikTok)
- **BR-002**: Each platform can provide one or more services
- **BR-003**: Only superadmin can configure (add/remove/enable/disable) platforms
- **BR-004**: Platforms can be enabled or disabled globally
- **BR-005**: Disabled platforms are not available for data scraping or folder creation

### 2. Service Management Rules
- **BR-006**: A service is a type of content that can be scraped (e.g., Posts, Reels, Comments, Profiles)
- **BR-007**: Each platform provides one or more services
- **BR-008**: Only superadmin can configure which services are available for each platform
- **BR-009**: Services can be enabled or disabled per platform
- **BR-010**: Disabled services are not available for data scraping or folder creation

### 3. User Permission Rules
- **BR-011**: Regular users can only see and use platforms that are configured and enabled by superadmin
- **BR-012**: Regular users can only see and use services that are configured and enabled for each platform
- **BR-013**: Users cannot create folders for platforms or services that are not available

### 4. Folder Creation Rules
- **BR-014**: Creating a data storage folder requires selecting an available platform
- **BR-015**: After selecting a platform, users must choose from available services for that platform
- **BR-016**: Folder creation is restricted to only configured and enabled platform-service combinations
- **BR-017**: Folder categories must match the selected service type

## Database Schema

### Models Created

#### 1. Platform Model
```python
class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., 'instagram', 'facebook'
    display_name = models.CharField(max_length=100)  # e.g., 'Instagram', 'Facebook'
    is_enabled = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. Service Model
```python
class Service(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., 'posts', 'reels', 'comments'
    display_name = models.CharField(max_length=100)  # e.g., 'Posts', 'Reels', 'Comments'
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 3. PlatformService Model
```python
class PlatformService(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['platform', 'service']
```

## API Endpoints

### Superadmin Endpoints (Require Superadmin Permission)

#### Platform Management
- `GET /api/users/platforms/` - List all platforms
- `POST /api/users/platforms/` - Create new platform
- `PUT /api/users/platforms/{id}/` - Update platform
- `DELETE /api/users/platforms/{id}/` - Delete platform

#### Service Management
- `GET /api/users/services/` - List all services
- `POST /api/users/services/` - Create new service
- `PUT /api/users/services/{id}/` - Update service
- `DELETE /api/users/services/{id}/` - Delete service

#### Platform-Service Management
- `GET /api/users/platform-services/` - List all platform-service combinations
- `POST /api/users/platform-services/` - Create new platform-service combination
- `PUT /api/users/platform-services/{id}/` - Update platform-service combination
- `DELETE /api/users/platform-services/{id}/` - Delete platform-service combination

### User Endpoints (Available to All Authenticated Users)

#### Available Platforms and Services
- `GET /api/users/available-platforms/` - Get enabled platforms with their services
- `GET /api/users/available-platforms/{id}/services/` - Get services for specific platform
- `GET /api/users/available-platforms/all_available/` - Get all available platform-service combinations

## Initial Data

The system comes pre-populated with the following data:

### Platforms
1. **Instagram** - Instagram social media platform
2. **Facebook** - Facebook social media platform
3. **LinkedIn** - LinkedIn professional network
4. **TikTok** - TikTok short-form video platform

### Services
1. **Posts** - Regular posts and content
2. **Reels** - Short-form video content
3. **Comments** - Comments on posts and content
4. **Profiles** - User profile information

### Platform-Service Combinations
- **Instagram**: Posts, Reels, Comments, Profiles
- **Facebook**: Posts, Reels, Comments
- **LinkedIn**: Posts, Profiles
- **TikTok**: Posts, Comments

## Management Commands

### Populate Initial Data
```bash
python manage.py populate_platforms_services
```

This command:
- Creates the initial platforms and services
- Sets up the platform-service combinations
- Associates all data with the first superuser found

## Frontend Integration

### API Service
Created `frontend/src/services/platformService.ts` with:
- TypeScript interfaces for all models
- API methods for all endpoints
- Utility functions for validation and data retrieval
- Error handling and type safety

### Key Features
- **Platform Validation**: Ensures only enabled platforms are available
- **Service Validation**: Ensures only enabled services for each platform are available
- **Dynamic UI**: Platform and service selection based on configuration
- **Permission-Based Access**: Different endpoints for superadmin vs regular users

## Usage Examples

### For Superadmins

#### Adding a New Platform
```python
# Via Django Admin
# Or via API
POST /api/users/platforms/
{
    "name": "twitter",
    "display_name": "Twitter",
    "description": "Twitter social media platform",
    "icon_name": "twitter",
    "color": "#1DA1F2"
}
```

#### Adding a New Service
```python
# Via Django Admin
# Or via API
POST /api/users/services/
{
    "name": "tweets",
    "display_name": "Tweets",
    "description": "Twitter posts and content",
    "icon_name": "article"
}
```

#### Creating Platform-Service Combination
```python
# Via Django Admin
# Or via API
POST /api/users/platform-services/
{
    "platform": 5,  # Twitter platform ID
    "service": 5,   # Tweets service ID
    "is_enabled": true,
    "description": "Twitter Tweets"
}
```

### For Regular Users

#### Getting Available Platforms
```javascript
import { platformServiceAPI } from '../services/platformService';

const platforms = await platformServiceAPI.getAvailablePlatforms();
// Returns only enabled platforms with their available services
```

#### Validating Platform-Service Combination
```javascript
const isValid = await platformServiceAPI.validatePlatformService('instagram', 'posts');
// Returns true if Instagram Posts is available
```

## Security and Permissions

### Permission Classes
- **IsSuperAdmin**: Custom permission class for superadmin-only endpoints
- **IsAuthenticated**: Standard DRF permission for user endpoints

### Data Filtering
- Regular users only see enabled platforms and services
- Superadmins can see all data but are restricted by permission classes
- Platform-service combinations are filtered by both platform and service enabled status

## Integration Points

### Data Storage Integration
The platform-service system integrates with the existing data storage system:
- Folder creation now requires valid platform-service combinations
- Folder categories must match the selected service type
- Data scraping jobs are restricted to available platform-service combinations

### BrightData Integration
The system works with the existing BrightData configuration:
- Platform names match the existing platform choices
- Service names correspond to content types
- Platform-service combinations determine available scraping options

## Future Enhancements

### Planned Features
1. **Platform-Specific Configuration**: Additional settings per platform
2. **Service Templates**: Predefined service configurations
3. **Usage Analytics**: Track platform and service usage
4. **Bulk Operations**: Mass enable/disable platform-service combinations
5. **Audit Logging**: Track configuration changes
6. **API Rate Limiting**: Platform-specific rate limits
7. **Cost Management**: Platform-specific pricing and quotas

### Migration Path
The system is designed to be backward compatible:
- Existing hardcoded platform choices are preserved
- Existing folder structures remain intact
- Gradual migration from hardcoded to configurable system

## Testing

### Test Coverage
- Model validation and relationships
- API endpoint permissions and responses
- Business rule enforcement
- Data integrity constraints
- Frontend integration

### Test Commands
```bash
# Run all tests
python manage.py test users.tests

# Run specific test
python manage.py test users.tests.PlatformServiceTestCase
```

## Deployment Notes

### Database Migration
```bash
python manage.py makemigrations users
python manage.py migrate
```

### Initial Setup
```bash
# Create superuser first
python manage.py createsuperuser

# Populate initial data
python manage.py populate_platforms_services
```

### Environment Variables
No additional environment variables required. The system uses existing Django settings.

## Conclusion

This implementation provides a robust, scalable platform and service management system that:
- Enforces business rules through database constraints and API permissions
- Provides flexible configuration for superadmins
- Ensures data integrity and security
- Maintains backward compatibility
- Supports future enhancements and scalability

The system is now ready for integration with the existing data storage and scraping workflows. 