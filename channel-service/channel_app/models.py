from django.db import models
import uuid

class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel_id = models.UUIDField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class VideoInPlaylistEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video_id = models.UUIDField()
    playlist_id = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# class WatchHistoryEntry(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_id = models.UUIDField()
#     video_id = models.UUIDField()
#     opened_at = models.DateTimeField()
#     closed_at = models.DateTimeField()

class SubscriberEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel_id = models.UUIDField()
    user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel_id = models.UUIDField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    public = models.BooleanField(default=True)
    file_id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

