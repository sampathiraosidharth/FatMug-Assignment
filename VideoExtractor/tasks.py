# tasks.py
from celery import shared_task
from .models import VideoModel2, Subtitles
import subprocess
import os
import pysrt


@shared_task
def extract_sub(video_id, video_path):
    try:
        subtitle_file = f'{video_path}.srt'
        command = [
            'ffmpeg', '-i', video_path,
            '-map', '0:s:0', '-y',
            subtitle_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to extract subtitles: {result.stderr}")

        if not os.path.exists(subtitle_file):
            raise Exception(f"Subtitle file not created: {subtitle_file}")


        subs = pysrt.open(subtitle_file)

        video = VideoModel2.objects.get(id=video_id)

        for sub in subs:
            start_seconds = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000
            content = sub.text

            Subtitles.objects.create(
                video=video,
                languages='en',
                file=f'{subtitle_file}',
                content=content,
                start_time=start_seconds
            )

        return f"Subtitles extracted successfully for video {video_id}"

    except Exception as e:
        print(f"Failed to extract subtitles: {e}")
        return f"Failed to extract subtitles for video {video_id}"
