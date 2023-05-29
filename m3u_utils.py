import os
import sys

sys.path.append("./")
# from calibre_plugins.AudioM3U.unzip import UNZIP_PATH
# from calibre.constants import plugins, iswindows, islinux, isosx

# from calibre_plugins.AudioM3U.unzip import install_libs
# sys.path.append(UNZIP_PATH)
print("m3u_util path",sys.path)
import mutagen

from mutagen.mp4 import MP4
from mutagen.mp3 import MP3

tagvals = {}
duration = 0.0

def get_metadata(file_path):
    """
    Extracts metadata from an audio file.
    Supports .mp3, .m4a, and .m4b formats.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    tagvals["type"] = file_extension[1:].upper()

    if file_extension == ".mp3":
        audio = MP3(file_path)
#        audio.info.pprint()
        if "TPE1" in audio:
            tagvals["author"] = audio["TPE1"][0]
        if "TALB" in audio:
            tagvals["title"] = audio["TALB"][0]
        if "TCOM" in audio:
            tagvals["narrator"] = audio["TCOM"][0]
        tagvals["sample_rate"] = audio.info.sample_rate
        tagvals["bitrate"] = audio.info.bitrate // 1000  # Bitrate in kbps
        if (audio.info.mode == 0):
            tagvals["mode"] = "Stereo"
        elif (audio.info.mode == 1):
            tagvals["mode"] = "Joint Stereo"
        elif (audio.info.mode == 2):
            tagvals["mode"] = "Dual Channel"
        elif (audio.info.mode == 3):
            tagvals["mode"] = "Mono"
        else:
            tagvals["mode"] = "Unknown"

    elif file_extension == ".m4a" or file_extension == ".m4b":
        audio = MP4(file_path)
#        audio.info.pprint()
        if "\xa9ART" in audio:
            tagvals["author"] = audio["\xa9ART"][0]
        if "\xa9alb" in audio:
            tagvals["title"] = audio["\xa9alb"][0]
        if "\xa9wrt" in audio:
            tagvals["narrator"] = audio["\xa9wrt"][0]
        tagvals["sample_rate"] = audio.info.sample_rate
        tagvals["bitrate"] = audio.info.bitrate // 1000  # Bitrate in kbps
        if (audio.info.channels == 1):
            tagvals["mode"] = "Mono"
        elif (audio.info.channels == 2):
            tagvals["mode"] = "Stereo"
        else:
            tagvals["mode"] = "Unknown"

def tally_metadata(file_path):
    global duration
    if "size" not in tagvals:
        tagvals["size"] = 0
    if "duration" not in tagvals:
        tagvals["duration"] = 0
    tagvals["size"] += os.path.getsize(file_path)
    audio = mutagen.File(file_path)
    duration += audio.info.length
    #print(f"Adding {int(audio.info.length)} seconds, total now {tagvals['duration']}")
    #print(f"duration is {duration}")

def playtime(seconds):
    """
    Takes seconds as an input and returns a formatted time string hh:mm:ss
    """
    #print (f"seconds: {type(seconds)}")
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return("{:0>1d}:{:0>2d}:{:0>2d}".format(hours,mins,seconds))

def extract_artwork(file_path):
    """
    Save cover artwork to a file (if available)
    """
    audio = mutagen.File(file_path)
    cover_art_filename = f"{tagvals['title']}_cover.jpg"
    #print("keys: ",audio.keys())
    if "covr" in audio:
        cover_art = audio["covr"][0]
        with open(cover_art_filename, "wb") as cover_art_file:
            cover_art_file.write(cover_art)

        print(f"Cover Artwork saved as: {cover_art_filename}")
    elif "APIC:" in audio:
        #cover_art = audio["APIC:"]
        cover_art = audio.get("APIC:").data
        with open(cover_art_filename, "wb") as cover_art_file:
            cover_art_file.write(cover_art)

        print(f"Cover Artwork saved as: {cover_art_filename}")
        
    else:
        print("No Cover Artwork found.")

def print_metadata():
    print(f"Author: {tagvals['author']}")
    print(f"Title: {tagvals['title']}")
    if "narrator" in tagvals:
        print(f"Narrator: {tagvals['narrator']}")
    print(f"Bitrate: {tagvals['bitrate']} kbps")
    print(f"Sample Rate: {tagvals['sample_rate']}")
    print(f"Mode: {tagvals['mode']}")
    print(f"Type: {tagvals['type']}")
    print(f"Total Running Seconds: {tagvals['duration']}")
    print(f"Total Running Length: {playtime(tagvals['duration'])}")
    print(f"Total Size: {tagvals['size']}")
    print("Total Size: {:.1f}M".format(tagvals['size'] / (1024*1024)))
    #print("Total Size: {:.1f}M".format(tagvals['size']))

def get_tags(playlist_path):
    """
    Analyzes a .m3u playlist and prints artist name, album name, bitrate,
    total running length, and saves the cover artwork to a file.
    """
    global tagvals
    global duration
    tagvals = {}
    duration = 0.0
    with open(playlist_path, "r") as playlist_file:
        lines = playlist_file.readlines()

        get_metadata(lines[0].strip())
        for line in lines:
            tally_metadata(line.strip())
        tagvals["duration"] += int(duration+.5) # Round floating point to integer
        #print(f"size was {tagvals['size']}")
        #tagvals["size"] = tagvals["size"] / (1024 * 1024) # Bytes to Megs
        #print(f"size now: {tagvals['size']}")
        print_metadata()
        #extract_artwork(lines[0].strip())
    #print("returning tagvals: ",tagvals)
    return tagvals

def get_cover(playlist_path):
    """
    Save cover artwork to a file (if available)
    """
    with open(playlist_path, "r") as playlist_file:
        lines = playlist_file.readlines()
        file_path = lines[0].strip()

    audio = mutagen.File(file_path)
    cover_art = None
    #print("keys: ",audio.keys())
    if "covr" in audio:
        cover_art = audio["covr"][0]
        #print(f"Cover Artwork found in covr")
    elif "APIC:" in audio:
        cover_art = audio.get("APIC:").data
        #print(f"Cover Artwork found in APIC:")
        
    return cover_art