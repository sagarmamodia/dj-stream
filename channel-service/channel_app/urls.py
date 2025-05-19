from django.urls import path, include
from . import views

urlpatterns = [
    path('channel/get_channel_info/<str:channel_id>/', views.get_channel_info),
    path('channel/get_channels/<str:user_id>/', views.get_all_channels),
    path('channel/get_all_videos/<str:channel_id>/', views.get_all_videos_of_channel),
    path('playlist/get_all/<str:channel_id>/', views.get_playlists_of_channel ),
    path('playlist/info/<str:playlist_id>/', views.get_playlist_info),
    path('playlist/get_vidoes/<str:playlist_id>/', views.get_videos_in_playlist),
    path('channel/create/', views.create_channel),
    path('channel/update_info/', views.update_channel_info),
    path('playlist/create/', views.create_playlist),
    path('playlist/update_info/', views.update_playlist_info),
    path('playlist/add_video/', views.add_video_in_playlist),
    path('playlist/remove_video/', views.remove_video_from_playlist),
    path('channel/upload_video_metadata/', views.upload_video_metadata),
]
