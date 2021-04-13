"""Mini Link
Is a link shortener system including following use-cases(APIs):
    - Creating account for each user (URL owner).
    - Analytics and reports for each individual URL by its owner.
    - Redirect guests(visitors) to the original URL.

Author: Maripillon (Faranak Heydari)
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
