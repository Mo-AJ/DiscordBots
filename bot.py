import discord
from discord.ext import commands
from datetime import datetime, timedelta
from pytube import YouTube
from moviepy.editor import concatenate_videoclips, VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.transitions import fadein, fadeout
import numpy as np

from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, afx

from moviepy.editor import VideoFileClip, CompositeVideoClip, afx, TextClip

import cv2


# Create the required intents object
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Helper function to check if a message contains a video link
def download_and_clip_youtube_video(url, filename):
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4').first()
    stream.download(filename=filename)

    clip = VideoFileClip(filename).subclip(0, 10)
    clipped_filename = f"clipped_{filename}"
    clip.write_videofile(clipped_filename)

    return clipped_filename

#def combine_videos(video_files, output_file):
  #  clips = [VideoFileClip(video) for video in video_files]
  #  final_clip = concatenate_videoclips(clips)
  #  final_clip.write_videofile(output_file)

import cv2
import numpy as np
from moviepy.editor import CompositeVideoClip, VideoFileClip, afx, concatenate_videoclips

def combine_videos(video_files, output_file, crossfade_duration=1):
    clips = [VideoFileClip(video) for video in video_files]

    # Apply fadein and fadeout effects to audio:
    crossfaded_audios = [clip.audio.fx(afx.audio_fadein, crossfade_duration).fx(afx.audio_fadeout, crossfade_duration) for clip in clips]

    # Apply fadein and fadeout effects to video:
    crossfaded_clips = [clip.crossfadein(crossfade_duration).crossfadeout(crossfade_duration) for clip in clips]

    # Apply text and crossfade audio to video clips:
    for idx, clip in enumerate(crossfaded_clips):
        clip.audio = crossfaded_audios[idx]
        
        # Apply text to each frame of the clip using opencv
        clip = clip.fl_image(lambda frame: add_text(frame, f"Clip {idx+1}"))

    # Adjusting start times for clips for crossfade effect:
    for idx in range(1, len(crossfaded_clips)):
        crossfaded_clips[idx] = crossfaded_clips[idx].set_start(crossfaded_clips[idx - 1].end - crossfade_duration)

    # Composite the clips together:
    final_clip = concatenate_videoclips(crossfaded_clips, method="compose")
    final_clip.write_videofile(output_file)

def add_text(frame, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    position = (frame.shape[1] - 100, 30)  # top right corner
    font_scale = 10
    font_color = (255, 255, 255)  # white
    font_thickness = 2

    frame_with_text = cv2.putText(np.array(frame), text, position, font, font_scale, font_color, font_thickness, cv2.LINE_AA)
    return frame_with_text


def contains_video_link(message):
    video_domains = ['youtube.com', 'youtu.be', 'vimeo.com']
    return any(domain in message.content for domain in video_domains)

# Event to log bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Command to fetch top 3 messages with video links based on reactions
@bot.command()
async def top3(ctx):
    one_month_ago = datetime.utcnow() - timedelta(days=30)

    # Fetching messages
    messages = []
    async for msg in ctx.channel.history(after=one_month_ago, limit=1000):
        messages.append(msg)

    # Filter messages that contain video links
    video_messages = [msg for msg in messages if contains_video_link(msg)]

    # Sorting video messages based on the sum of their reactions' count
    sorted_messages = sorted(video_messages, key=lambda msg: sum(reaction.count for reaction in msg.reactions), reverse=True)
    top_messages = sorted_messages[:3]  # Get the top 3 messages

    for idx, message in enumerate(top_messages, 1):
        reaction_count = sum(reaction.count for reaction in message.reactions)
        await ctx.send(f"Top {idx}: {message.jump_url} with {reaction_count} reactions.")

@bot.listen('on_message')
async def on_message(message):
    # Make sure the bot doesn't reply to itself
    if message.author == bot.user:
        return

    # Check if the message is a command, if so, just return and don't process
    if message.content.startswith(bot.command_prefix):
        return

    # If the message content is "hi", reply with "hi"
    if message.content.lower() == "hi":
        await message.channel.send("hi")



@bot.command()
async def postvideos(ctx):
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    messages = []
    async for msg in ctx.channel.history(after=one_month_ago, limit=1000):
        messages.append(msg)

    video_messages = [msg for msg in messages if contains_video_link(msg)]
    sorted_messages = sorted(video_messages, key=lambda msg: sum(reaction.count for reaction in msg.reactions), reverse=True)
    top_messages = sorted_messages[:3]

    # Download, clip, and combine the videos
    downloaded_clips = []
    for idx, message in enumerate(top_messages, 1):
        url = message.content
        filename = f"video_{idx}.mp4"
        try:
            clipped_file = download_and_clip_youtube_video(url, filename)
            downloaded_clips.append(clipped_file)
        except Exception as e:
            await ctx.send(f"Error processing video {idx}: {e}")
    
    
    if downloaded_clips:
        combined_file = "final_video.mp4"
        combine_videos(downloaded_clips, combined_file)
        await ctx.send("Here are the top 3 videos combined:", file=discord.File(combined_file))

bot.run('MTE0MzM3NjUwMDU1NzYzMTU4OQ.GjrGVR.goFBQYgEgRYlhn0yEMwkTtl_m8MWKMzYT18AMs')
