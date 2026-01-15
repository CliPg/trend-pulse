from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from os import getenv

video_id = "xIFkrVU5Krk"

try:
    ytt_api = YouTubeTranscriptApi(
        proxy_config=WebshareProxyConfig(
            proxy_username=getenv("WEBSHARE_PROXY_USERNAME"),
            proxy_password=getenv("WEBSHARE_PROXY_PASSWORD"),
        )
    )

    # all requests done by ytt_api will now be proxied through Webshare
    transcript = ytt_api.fetch(video_id)
    print(transcript)
except Exception as e:
    print(f"Error fetching transcript: {e}")

