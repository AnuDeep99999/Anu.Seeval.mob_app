from django.urls import path
from .views import upload_mcq_excel, upload_success

urlpatterns = [
    path('upload-mcq/', upload_mcq_excel, name='upload-mcq'),
    path('upload-success/', upload_success, name='upload-success'),
]
