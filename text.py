from moviepy.editor import VideoFileClip, TextClip
import os
print(os.getcwd())


def add_text_with_moviepy(input_video_path, output_video_path, text):
    # Load the video clip
    clip = VideoFileClip(input_video_path)

    # Create a TextClip with the desired parameters
    txt_clip = TextClip(text, fontsize=24, color='white').set_pos(('right', 'top')).set_duration(clip.duration)

    # Overlay the text clip on the first video clip
    video_with_text = clip.fx(vfx.composite, txt_clip)

    # Write the result to a new file
    video_with_text.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

# Example usage:
current_path = os.getcwd()
input_path = os.path.join(current_path, "clipped_video_1.mp4")

print(input_path)
#input_path = "path_to_your_input_video.mp4"
output_path = os.path.join(current_path, "done_1.mp4")
text_to_add = "If I lose it all"
add_text_with_moviepy(input_path, output_path, text_to_add)


