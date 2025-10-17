from django.urls import path
from . import views

urlpatterns = [
    path("", views.video_list, name="video_list"),
    path("videos/<int:pk>/", views.video_detail, name="video_detail"),
    path("videos/create/", views.video_create, name="video_create"),
    path("videos/<int:pk>/update/", views.video_update, name="video_update"),
    path("videos/<int:pk>/delete/", views.video_delete, name="video_delete"),
]
