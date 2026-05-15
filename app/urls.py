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
]
