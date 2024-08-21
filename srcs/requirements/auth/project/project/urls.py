"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from django.urls import include, path
from authentification import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin', admin.site.urls),
    path('auth/token/refresh', views.refreshToken, name='token_refresh'), 
    path('auth/login', views.login),
    path('auth/signup', views.signup),
    path('auth/logout', views.logout),
    path('auth/login42', views.login42),
    path('auth/updateEmail', views.updateEmail),
    path('auth/updateUsername', views.updateUsername),
    path('auth/updatePassword', views.updatePassword),
    path('auth/updateAvatar', views.updateAvatar),
    path('auth/userInfos', views.userInfos),
    path('auth/friendList', views.friendList),
    path('auth/friendRequest', views.friendRequest),
    path('auth/acceptFriendRequest', views.acceptFriendRequest),
    path('auth/declineFriendRequest', views.declineFriendRequest),
    path('auth/gameHistory', views.gameHistory),
    path('local/gameResult', views.gameResult),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
