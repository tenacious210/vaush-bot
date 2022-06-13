from youtube_transcript_api import YouTubeTranscriptApi

with open("transcript.txt", "a") as transcript_file:
    for line_dict in YouTubeTranscriptApi.get_transcript(""):
        print(f'Writing "{line_dict["text"]}')
        transcript_file.write(f'{line_dict["text"]} ')
