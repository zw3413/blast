import ffmpeg

def get_video_info_ffmpeg(file_path: str):
    try:
        probe = ffmpeg.probe(file_path)
        video_info = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        return video_info
    except Exception as e:
        return str(e)