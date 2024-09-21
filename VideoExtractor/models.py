from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        abstract = True
class VideoModel1(BaseModel):
    video_name = models.TextField(help_text="Name of the video",null=False,blank=False)
    video_path = models.TextField(help_text="Path for the video saved in the local server",null=False,blank=False)

    class Meta:
        db_table = 'VideoModel1'

class VideoModel2(BaseModel):
    video_name = models.TextField(help_text="Name of the video",null=False,blank=False)
    video_file = models.FileField(upload_to="video")

    class Meta:
        db_table = 'VideoModel2'

class Subtitles(models.Model):
    video = models.ForeignKey(VideoModel2, on_delete=models.CASCADE, related_name='subtitles')
    languages = models.TextField()
    file = models.TextField()
    content = models.TextField()
    start_time = models.FloatField()

    class Meta:
        db_table = 'Subtitles'