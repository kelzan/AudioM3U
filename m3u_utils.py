__license__   = 'GPL v3'
__copyright__ = '2023, Kelly Larson'

import os
import sys

#sys.path.append("./")
# from calibre_plugins.AudioM3U.unzip import UNZIP_PATH
# from calibre.constants import plugins, iswindows, islinux, isosx

# from calibre_plugins.AudioM3U.unzip import install_libs
# sys.path.append(UNZIP_PATH)
#print("m3u_util path",sys.path)
import calibre_plugins.AudioM3U.mutagen

from calibre_plugins.AudioM3U.mutagen.mp4 import MP4, MP4Cover
from calibre_plugins.AudioM3U.mutagen.mp4 import AtomDataType
from calibre_plugins.AudioM3U.mutagen.mp3 import MP3
from calibre_plugins.AudioM3U.mutagen.id3 import ID3, APIC
from calibre_plugins.AudioM3U.mutagen import File

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
        if "TCON" in audio:
            tagvals["genre"] = audio["TCON"][0]
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
        # audio = ID3(file_path)
        # print(f"tags: {audio.keys()}")

    elif file_extension == ".m4a" or file_extension == ".m4b":
        audio = MP4(file_path)
#        audio.info.pprint()
        if "\xa9ART" in audio:
            tagvals["author"] = audio["\xa9ART"][0]
        if "\xa9alb" in audio:
            tagvals["title"] = audio["\xa9alb"][0]
        if "\xa9wrt" in audio:
            tagvals["narrator"] = audio["\xa9wrt"][0]
        if "\xa9gen" in audio:
            tagvals["genre"] = audio["\xa9gen"][0]
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
    if "num_files" not in tagvals:
        tagvals["num_files"] = 0
    tagvals["size"] += os.path.getsize(file_path)
    tagvals["num_files"] += 1
    audio = File(file_path)
    duration += audio.info.length
    # print(f"Adding {int(audio.info.length)} seconds, total now {tagvals['duration']}")
    # print(f"duration is {duration}")

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
    audio = File(file_path)
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
    if "author" in tagvals:
        print(f"Author: {tagvals['author']}")
    if "title" in tagvals:
        print(f"Title: {tagvals['title']}")
    if "narrator" in tagvals:
        print(f"Narrator: {tagvals['narrator']}")
    if "genre" in tagvals:
        print(f"Genre: {tagvals['genre']}")
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

def set_cover(file_path, cover_info):
    file_extension = os.path.splitext(file_path)[1].lower()
    tagvals["type"] = file_extension[1:].upper()

    if file_extension == ".mp3":
        audio = ID3(file_path)
        if audio.getall('APIC'):
            audio.delall('APIC')
        #mime = "image/"+cover_info[0]
        #print(f"mime: {mime}")
        apic = APIC(type=3, mime="image/"+cover_info[0], desc="Cover", data=cover_info[1])
        audio.add(apic)
        audio.save()
        #audio.add(APIC(3, "image/"+cover_info[0], 'Cover', cover_info[1]))
        #audio.save()

    elif file_extension == ".m4a" or file_extension == ".m4b":
        audio = MP4(file_path)
        print(f"format: {cover_info[0]}")
        if (cover_info[0] == "jpeg"):
            audio["covr"] = [ MP4Cover(cover_info[1], imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()
            print("Saved")
        elif (cover_info[1] == "png"):
            audio["covr"] = [ MP4Cover(cover_info[1], imageformat=MP4Cover.FORMAT_PNG)]
            audio.save()



def get_cover(playlist_path):
    """
    Save cover artwork to a file (if available)
    """
    with open(playlist_path, "r") as playlist_file:
        lines = playlist_file.readlines()
        file_path = lines[0].strip()

    audio = File(file_path)
    cover_art = None
    mime = None
    #print("keys: ",audio.keys())
    if "covr" in audio:
        cover_art = audio["covr"][0]
        if (audio["covr"][0].imageformat == AtomDataType.PNG):
            mime = "png"
        else:
            mime = "jpeg"
        #print(f"[1] = {audio['covr'][1]}")
        #print(f"Cover Artwork found in covr")
    else:
        apics = [item for item in audio.keys() if item.startswith("APIC:")]
        #print(f"apics: {apics}")
        if (len(apics) > 0):
            # Could possibly have multiple artwork tags, so just grab the first one
            cover_art = audio.get(apics[0]).data
            mime = audio.get(apics[0]).mime
            if mime.startswith('image/'):
                mime = mime[6:]        
            #print(f"cover_type: {cover_type}")
            #print(f"Cover Artwork found in APIC:")
    print(f"mime: {mime}")       
    return ( (mime, cover_art) )

def export_tags(playlist_path, update_fields):
    keys = list(update_fields.keys())
    #print(f"keys: {keys}")
    with open(playlist_path, "r") as playlist_file:
        for line in playlist_file:
            line = line.strip()
            if line and not line.startswith('#'):
                audio = File(line, easy=True)
        #        audio.info.pprint()
                if "author" in keys:
                    audio["artist"] = update_fields["author"]
                if "title" in keys:
                    audio["album"] = update_fields["title"]
                if "narrator" in keys:
                    audio["composer"] = update_fields["narrator"]
                if "genre" in keys:
                    audio["genre"] = update_fields["genre"]
                #if "cover" in keys:
                #    audio["covr"] = update_fields["cover"]
                #audio.info.pprint()
                #print("SAVING!")
                audio.save()
                if "cover" in keys:
                    set_cover(line, update_fields["cover"])

def create_m3u(book_directory):
    # Retrieve all audio files in the book directory
    audio_files = [
        file
        for file in os.listdir(book_directory)
        if file.lower().endswith((".mp3", ".wma", ".m4a", ".m4b"))
    ]

    # Sort the audio files alphabetically
    audio_files.sort()
    m3u = []

    for audio_file in audio_files:
        m3u.append(os.path.join(book_directory, audio_file))
        #file_path = file_path.replace("\\","/")

    #print(f"M3U created: {m3u}")
    return m3u