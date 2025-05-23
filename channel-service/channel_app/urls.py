from django.urls import path, include
from . import views

urlpatterns = [
    path('info/<str:channel_id>/', views.get_channel_info),
    path('user/get_channels/<str:user_id>/', views.get_all_channels),
    path('video/get_all/<str:channel_id>/', views.get_all_videos_of_channel),
    path('playlist/get_all/<str:channel_id>/', views.get_playlists_of_channel ),
    path('playlist/info/<str:playlist_id>/', views.get_playlist_info),
    path('playlist/get_videos/<str:playlist_id>/', views.get_videos_in_playlist),
    path('auth_required/create/', views.create_channel),
    path('auth_required/update_info/', views.update_channel_info),
    path('auth_required/playlist/create/', views.create_playlist),
    path('auth_required/playlist/add_video/', views.add_video_in_playlist),
    path('auth_required/video/upload_metadata/', views.upload_video_metadata),

]
