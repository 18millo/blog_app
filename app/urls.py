from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('blogs/', views.bloglist, name='blog_list'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('add-blog/', views.add_blog, name='add_blog'),
    path('profile/', views.profile, name='profile'),
    path('enable-2fa/', views.enable_2fa, name='enable_2fa'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/blogs/', views.admin_manage_blogs, name='admin_manage_blogs'),
    path('admin-panel/blogs/<int:blog_id>/delete/', views.admin_blog_delete, name='admin_blog_delete'),
    path('admin-panel/users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin-panel/users/<int:user_id>/toggle-role/<str:group_name>/', views.admin_toggle_role, name='admin_toggle_role'),
]
