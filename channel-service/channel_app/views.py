from django.shortcuts import render
from django.http import JsonResponse
from .models import Channel, Playlist, VideoInPlaylistEntry, Video
import json
from django.conf import settings
import requests
from .utils import parse_auth_headers
from django.views.decorators.csrf import csrf_exempt
from .rabbitmq import get_channel
import pika

def home(request):
    return JsonResponse({"res": "Welcome to channel_service"})

def get_channel_info(request, channel_id):
    try:
        channel = Channel.objects.filter(id=channel_id).first()
    except:
        return JsonResponse({"error": "Failed to fetch channel data from database"}, status=501)

    if(channel is None):
        return JsonResponse({"error": "Channel not found"}, status=404)
    
    response = {
            "id": channel.id,
            "name": channel.name,
            "description": channel.description,
            "user_id": channel.user_id,
            "created_at": channel.created_at
    }

    return JsonResponse(response, status=200)

def get_all_channels(request, user_id):
    try:
        channel_list = Channel.objects.filter(user_id=user_id)
    except:
        return JsonResponse({"error": "Internal server error"}, status=501)

    response = { "channel_list": [] }
    for channel in channel_list: 
        channel_dict = {
                "id": channel.id,
                "name": channel.name,
                "description": channel.description,
                "user_id": channel.user_id,
                "created_at": channel.created_at
        }
        response["channel_list"].append(channel_dict)

    return JsonResponse(response, status=200)

def get_all_videos_of_channel(request, channel_id):
    try:
        video_entry_list = Video.objects.filter(channel_id=channel_id)
    except:
        return JsonResponse({"error": "Failed to fetch video_entries from database"}, status=501)
    
    response = {
        "videos": []
    }

    for video_obj in video_entry_list:
        video_dict = {
            "id": str(video_obj.id),
            "channel_id": str(video_obj.channel_id),
            "title": video_obj.title,
            "description": video_obj.description,
            "file_id": video_obj.file_id
        }
        response['videos'].append(video_dict)


    return JsonResponse(response, status=200)

def get_searched_channel(request, search_query):
    pass

def get_playlists_of_channel(request, channel_id):
    """
    Response data format
    {
        id 
        name 
        description 
        created_at 
    }
    """
    try:
        playlist_list = Playlist.objects.filter(channel_id=channel_id)
    except:
        return JsonReponse({"error": "Failed to fetch playlists from database"}, status=501)
    
    response = {
        "playlists": []
    }

    for playlist in playlist_list:
        playlist_dict = {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "created_at": playlist.created_at
        }
        response['playlists'].append(playlist_dict)

    return JsonResponse(response, status=200)

def get_playlist_info(request, playlist_id):
    try:
        playlist = Playlist.objects.filter(id=playlist_id).first()
    except:
        return JsonResponse({"error": "Failure to fetch playlist info from database"}, status=500)
    
    response = {
        "id": playlist.id,
        "channel_id": playlist.channel_id,
        "name": playlist.name,
        "description": playlist.description,
        "created_at": playlist.created_at
    }

    return JsonResponse(response)

def get_videos_in_playlist(request, playlist_id):
    try:
        video_list = VideoInPlaylistEntry.objects.filter(playlist_id=uuid.UUID(playlist_id))
    except:
        return JsonResponse({"error": "Failure to fetch videos from database."}, status=500)

    response = {
        "video_list": []
    }

    for video_obj in video_list:
        video_dict = {
            "id": str(video_obj.id),
            "channel_id": str(video_obj.channel_id),
            "title": video_obj.title,
            "description": video_obj.description,
            "file_id": video_obj.file_id
        }
        response['video_list'].append(video_dict)

    return JsonResponse(response)


@csrf_exempt
@parse_auth_headers
def create_channel(request):
    """
    Post data format
    {
        name:
        description: 
    }

    Response data format
    {
        id:
    }
    """
    if request.method=="POST":
        user_id = request.user_id
        print(user_id, request.user_name, request.user_email)
        try:
            data = json.loads(request.body)
            channel_name = data['name']
            channel_desc = data['description']
        except:
            return JsonResponse({"error": "Incorrect post data format"}, status=400)
       
        try:
            channel= Channel.objects.create(user_id=user_id, name=channel_name, description=channel_desc)
        except:
            return JsonResponse({"error": "Failed to create channel in database"}, status=501)

        return JsonResponse({'id': channel.id}, status=200)

    else:
        return JsonResponse({'error': 'Only post requests are allowed'}, status=400)

    
def update_channel_info(request):
    pass

@csrf_exempt
@parse_auth_headers
def create_playlist(request):
    """
    Post data format
    {
        channel_id
        name
        description
    }

    Response data format
    {
        playlist_id
    }
    """
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            channel_id = data['channel_id']
            name = data['name']
            desc = data['description']
        except:
            return JsonResponse({"error": "Invalid data format"}, status=400)

        # check if the logged in user is the owner of the channel or not
        if(request.user_id is None):
            return JsonResponse({"error": "Request is not authenticated"}, status=401)

        try:
            channel = Channel.objects.filter(id=channel_id).first()
        except:
            return JsonResponse({"error": "Failure to fetch channel from database"}, status=500)
        
        if(channel is None):
            return JsonResponse({"error": "Channel does not exist"}, status=400)

        if(str(channel.user_id) != request.user_id):
            return JsonResponse({"error": "You are not the owner of this channel."}, status=401)

        try:
            playlist = Playlist.objects.create(channel_id=channel_id, name=name, description=desc)
        except:
            return JsonResponse({"error": "Failed to create playlist in database"}, status=500)
        
        return JsonResponse({"playlist_id": playlist.id})
    
    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=400)

def update_playlist_info(request):
    pass

def add_video_in_playlist(request):
    """
    Post data format
    {
        playlist_id 
        video_id
    }

    Response data format
    {
        status: 'success'
    }
    """

    if request.method == "POST":
        try:
            data = json.loads(request.data)
            playlist_id = data['playlist_id']
            video_id = data['video_id']
        except:
            return JsonResponse({"error": "Invalid data format"}, status=400)
        
        user_id = request.user.id
        # check if the authenticated user is the owner of the playlist
        playlist = Playlist.objects.filter(id=playlist_id).first()
        if playlist is None:
            return JsonResponse({"error": "Playlist not found in database"}, status=400)

        if user_id != playlist.user_id:
            return JsonResponse({"error": "You are not the owner of this playlist"}, status=401)
        
        try:
            VideoInPlaylistEntry.objects.create(playlist_id=playlist_id, video_id=video_id)
        except:
            return JsonResponse({"error": "Failed to add video to playlist in database"}, status=500) 
        return JsonResponse({"status": "success"}, status=200)

    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=400)

def remove_video_from_playlist(request):
    """
    Post data format
    {
        playlist_id
        video_id
    }

    Response data format
    {
        status: success
    }
    """
    if request.method == "POST":
        try:
            data = json.loads(request.data)
            playlist_id = data['playlist_id']
            video_id = data['video_id']
        except:
            return JsonResponse({"error": "Invalid data format"}, status=400)
        
        user_id = request.user.id
        # check if the authenticated user is the owner of the playlist
        try:
            playlist = Playlist.objects.filter(id=playlist_id).first() 
        except: 
            return JsonResponse({"error": "Failed to fetch playlist from database"}, status=500)     
    
        if playlist is None:
            return JsonResponse({"error": "Playlist not found in database"}, status=400)

        if user_id != str(playlist.user_id):
            return JsonResponse({"error": "You are not the owner of this playlist"}, status=401)
        
        try:
            entry = VideoInPlaylistEntry.objects.filter(playlist_id=playlist_id, video_id=video_id).first()
            entry.delete()
        except:
            return JsonResponse({"error": "Failed to delete video from playlist in database"}, status=500) 
        return JsonResponse({"status": "success"}, status=200)

    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=400)

@csrf_exempt
@parse_auth_headers
def upload_video_metadata(request):
    """
    Post data format
    {
        channel_id
        title
        description
        public
        file_id(in mongodb)
    }

    Response data format
    {
        video_id
    }
    """
    if request.method=="POST":
        try:
            payload = json.loads(request.body)
            channel_id = payload['channel_id']
            title = payload['title']
            desc = payload['description']
            public = payload['public']
            file_id = payload['file_id']
        except:
            return JsonResponse({"error": "Invalid data format."}, status=400)

        try:
            channel = Channel.objects.get(id=channel_id)
        except:
            return JsonResponse({"error": f"Channel with {channel_id} does not exist."}, status=400)


        #check if the authenticated user is the owner of the file_id

        #check if file_id exists in mongodb database

        #store metadata 
        try:
            video, created = Video.objects.get_or_create(channel_id=channel_id, title=title, description=desc, public=public, file_id=file_id)
        except:
            return JsonResponse({"error": "Failure to put video metadata in the database"}, status=500)

        message_for_queue = {
            "event": "video_uploaded",
            "channel_id": str(channel.id),
            "channel_name": channel.name, 
            "video_id": str(video.id),
            "title": video.title 
        }
        
        try:
            channel = get_channel()
            channel.basic_publish(
                exchange='',
                routing_key=settings.EVENTS_QUEUE,
                body=json.dumps(message_for_queue),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except:
            print("Failure to put video uploaded message on the queue")
        
        return JsonResponse({"video_id": str(video.id)})

    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=400)


def get_searched_video(request, search_query):
    pass

def get_video_recommendations(request):
    pass

