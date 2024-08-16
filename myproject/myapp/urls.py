from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import password_reset_request, password_reset_confirm



urlpatterns = [
    path('home/',views.home, name='home'),
    path('',views.login, name='login'),
    path('signup/',views.signup, name='signup'),
    path('add/',views.createprod, name='createprod'),
    path('showall/',views.showall, name='showall'),
    path('delete/<int:id>',views.deleteprod, name='deleteprod'),
    path('edit/<int:id>/', views.editprod, name='editprod'),
    path('details/<int:id>/', views.prod_details, name='prod_details'),
    path('deleteall/', views.deleteall, name='deleteall'),
    path('logout/',views.logout,name='logout'),
    path('reset/', password_reset_request, name='password_reset_request'),
    path('confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('add-category/', views.add_category, name='add_category'),
    path('list-categories/', views.list_categories, name='list_categories'),
    path('delete-category/<int:id>/', views.delete_category, name='delete_category'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
