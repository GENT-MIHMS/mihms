from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("facilities/", views.facility_list, name="facility_list"),
    path("facilities/new/", views.facility_create, name="facility_create"),
    path("facilities/<int:pk>/", views.facility_detail, name="facility_detail"),
]
