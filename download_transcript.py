from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from youtube_transcript_api.formatters import TextFormatter

video_id = "fbQvVS_8ZNI"
transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
#transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
transcript = transcript_list.find_transcript(['en'])
translated = transcript.translate('ro')
formatter1 = JSONFormatter()
formatter2 = TextFormatter()
print(translated.fetch())
json_formatted = formatter1.format_transcript(translated.fetch())
text_formatted = formatter2.format_transcript(translated.fetch())
with open('your_filename.json', 'w', encoding='utf-8') as data:
    data.write(text_formatted)

