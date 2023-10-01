import youtube_dl

def download_video(url, output_directory='.'):
    ydl_opts = {
        'format': 'best',  # download the best quality
        'outtmpl': f'{output_directory}/%(title)s.%(ext)s',  # set download path and naming convention
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Example:
url_to_download = 'https://www.gifyourgame.com/WobblingOnstageMithra'
download_video(url_to_download)
