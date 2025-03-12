from django.urls import path
from .views import dispatch_dashboard, admin_login, admin_logout

urlpatterns = [
    path("dashboard/", dispatch_dashboard, name="dispatch_dashboard"),
    path("admin-login/", admin_login, name="admin_login"),
    path("admin-logout/", admin_logout, name="admin_logout"),
]
