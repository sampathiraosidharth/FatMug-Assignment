import os
import time
import uuid

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status,response
from rest_framework.views import APIView
from logging import getLogger
from VideoProcessor import settings
from .models import VideoModel2,VideoModel1,Subtitles
from .tasks import extract_sub
from django.core.serializers import serialize
from django.http import FileResponse
from django.shortcuts import get_object_or_404

logger = getLogger(__name__)


class VideoApi(APIView):
    def get(self, request):
        return render(request, 'upload_video1.html')

    def post(self,request):
        video_name = request.data.get("Name")
        video_file = request.FILES["Video"]
        if video_file:
            video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_file.name)
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            with open(video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            object = VideoModel1(video_name= video_name ,video_path=video_path)
            object.save()
            logger.info("File Saved to the Destination")
            return JsonResponse({'Message':'Sucessfully Got the video'},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'Message':'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)

class VideoApi2(APIView):
    def get(self, request):
        return render(request, 'upload_video2.html')

    def post(self,request):
        video_name = request.data.get("Name")
        # video_name= video_name+'_'+str(time.time()).split('.')[0]
        video_file = request.FILES["Video"]
        if video_file:
            object = VideoModel2(video_name=video_name,video_file=video_file)
            object.save()
            extract_sub.apply_async((object.id, object.video_file.path), countdown=1)
            logger.info("File Saved to the Destination")
            return JsonResponse({'Message':'Sucessfully Got the video'},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'Message':'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)

class GetData(APIView):
    def get(self, request):
        return render(request, 'get_data.html')

    def post(self, request):
        if request.data.get("table") == "1":
            all_entries = VideoModel1.objects.all()
        elif request.data.get("table") == "2":
            all_entries = VideoModel2.objects.all()
        else:
            return JsonResponse({'Message': 'Invalid table selection'}, status=status.HTTP_400_BAD_REQUEST)
        data = serialize('json', all_entries)
        return JsonResponse({'data': data, 'Message': 'Successfully Got the data'}, status=status.HTTP_200_OK)

class VideoDetailView(APIView):
    def get(self, request, video_id):
        video = VideoModel2.objects.get(id=video_id)
        subtitles = video.subtitles.all()
        query = request.GET.get('query', '')
        return render(request, 'video_detail.html', {'video': video, 'subtitles': subtitles, 'query': query})



class SearchSubtitles(APIView):
    def get(self, request):
        query = request.GET.get('q')
        results = []
        if query:
            print(f"Search Query: {query}")
            results = Subtitles.objects.filter(content__icontains=query)
            print(f"Results: {results}")
        return render(request, 'search_results.html', {'results': results, 'query': query})



class VideoListView(APIView):
    def get(self, request):
        videos = VideoModel2.objects.all()
        return render(request, 'video_list.html', {'videos': videos})



def stream_video(request, video_id):
    video = get_object_or_404(VideoModel2, id=video_id)
    response = FileResponse(open(video.video_file.path, 'rb'), content_type='video/mp4')
    response['Content-Disposition'] = f'inline; filename="{video.video_name}"'
    return response

def video_detail(request, video_id):
    video = get_object_or_404(VideoModel2, id=video_id)
    subtitles = Subtitles.objects.filter(video_id=video_id).order_by('start_time')


    subtitle_list = [{
        'start_time': subtitle.start_time,
        'content': subtitle.content,
        'language': subtitle.languages
    } for subtitle in subtitles]

    timestamp = request.GET.get('timestamp', 0)
    query = request.GET.get('query', '')

    context = {
        'video': video,
        'subtitles': subtitle_list,
        'timestamp': timestamp,
        'query': query
    }
    return render(request, 'videos/video_detail.html', context)


def srt_to_vtt(srt_file_path):
    vtt_file_path = srt_file_path.replace('.srt', '.vtt')
    with open(srt_file_path, 'r', encoding='utf-8') as srt_file:
        lines = srt_file.readlines()

    with open(vtt_file_path, 'w', encoding='utf-8') as vtt_file:
        vtt_file.write("WEBVTT\n\n")
        for line in lines:

            if '-->' in line:
                line = line.replace(',', '.')
            vtt_file.write(line)

    return vtt_file_path


def video_player(request, video_id):

    video = get_object_or_404(VideoModel2, id=video_id)
    srt_file_path = os.path.join(settings.MEDIA_ROOT, str(video.subtitles.file))


    vtt_file_path = srt_to_vtt(srt_file_path)

    context = {
        'video': video,
        'vtt_file_path': vtt_file_path,
    }
    return render(request, 'video_player.html', context)

