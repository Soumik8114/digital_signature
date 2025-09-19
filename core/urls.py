from . import views
from .views import UserFileListView
from django.urls import path

urlpatterns=[
    path('', views.home, name='sign-home'),
    path('about/',views.about,name='sign-about'),
    path('upload/', views.upload_view, name='upload_action'),
    path('uploads/', UserFileListView.as_view(), name='user_file_list'),
    path('sign-file/', views.sign_file_view, name='sign_file'),
    path('download-signature/<int:file_id>/', views.download_signature_view, name='download_signature'),
    path('verify/',views.verify_signature_view, name='verify_signature'),
    path('delete-file/<int:file_id>/', views.delete_file_view, name='delete_file'),
]