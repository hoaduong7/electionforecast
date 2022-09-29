"""electionforecast URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path
from main_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('constituency/<id>/<raw_name>', views.constituency),
    path('party/<id>/<name>', views.party),
    path('region/<id>', views.region),
    path('prediction/', views.prediction),
    path('update-prediction/', views.update_prediction),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_request, name="logout"),
    path("login/", views.login_request, name="login"),
    path("user/<username>", views.get_user_profile, name="get_user_profile"),
    path("user-prediction/", views.new_prediction, name="new_prediction"),
    path("user-prediction/<id>", views.prediction_splash, name="prediction_splash"),
    path("tutorial/", views.tutorial, name="tutorial"),
]
