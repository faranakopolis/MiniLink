"""Mini Link
It's a link shortener system including following use-cases(APIs):
    - Creating account for each user (URL owner)
    - Monitoring analytics and reports for each individual URL by its owner

Author: Maripillon (Faranak Heydari)
"""

"""miniLink URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from miniLink.core.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v01/user/signup/', SignUpView.as_view(), name='user_register'),

    path('api/v01/user/login/', TokenObtainPairView.as_view(), name='user_get_token'),
    path('api/v01/user/token/refresh/', TokenRefreshView.as_view(), name='user_token_refresh'),
    path('api/v01/user/logout/', LogoutView.as_view(), name='user_logout'),

    path('api/v01/user/createLink/', UrlView.as_view(), name='create_short_url'),

    path('api/v01/user/analytics/<int:url_id>', AnalyticsView.as_view(), name='analytics'),

    path('ml/<str:hashed_string>', RedirectView.as_view(), name='redirect_hashed_to_original'),

]
