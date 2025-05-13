"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/data-collector/", include("data_collector.urls")),
    path("api/query-builder/", include("query_builder.urls")),
    path("api/instagram-data/", include("instagram_data.urls")),
    path("api/facebook-data/", include("facebook_data.urls")),
    path("api/track-accounts/", include("track_accounts.urls")),
    path("api/linkedin-data/", include("linkedin_data.urls")),
    path("api/tiktok-data/", include("tiktok_data.urls")),
    path("api/brightdata/", include("brightdata_integration.urls")),
    path("api/", RedirectView.as_view(url="/api/users/", permanent=False)),
]
