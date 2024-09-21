from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('Video/',views.VideoApi.as_view(),name = "Video Extractor"),
    path('Video2/',views.VideoApi2.as_view(),name = "Video Extractor ORM Based"),
    path('GetData/',views.GetData.as_view(),name = "Checkdata"),
    path('video/<int:video_id>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('search/', views.SearchSubtitles.as_view(), name='search_subtitles'),
    path('videos/', views.VideoListView.as_view(), name='video_list'),
    path('stream/<int:video_id>/', views.stream_video, name='stream_video'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
