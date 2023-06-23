# AudioM3U
## Overview
AudioM3U is a plugin for Calibre which adds support for audiobook audio files through the use of M3U playlist files. 
The M3U file format is a simple text file containing the path to all of the audiofiles in the audiobook. The audio files
themselves are stored elsewhere, outside of the Calibre library. The plugin
will help you create or update an M3U file for new or existing books. Supported audiofile formats include 
MP3, M4A and M4B.

## Importing Metadata
Once the M3U format has been added to a book,
the plugin will then allow you to import metadata directly from the audiofiles into Calibre.

Imported metadata includes:
- Title
- Author
- Cover artwork
- Narrator
- Total playtime
- Total size
- Sample Rate
- Bitrate
- Mode (Mono, Stereo, etc.)
- File Type (MP3, M4A, M4B)
- Number of Audio Files
- Genre

## Exporting Metadata
The plugin will also allow you to export metadata from Calibre to the audiobook audio files.

Exported metadata includes:
- Title
- Author
- Cover artwork
- Narrator
- Genre

## Other Features

Other features of the plugin include:
- Ability to browse M3U file contents from within the GUI.
- Ability to verify the integrity of M3U file paths, as well as check for duplicated audio files.

## Acknowledgements
Calibre is an awesome program for managing any kind of book collection. 

You can download this here:
* (https://calibre-ebook.com/)

All audiofile handling in this plugin is done through the 'mutagen' library. 

More information here:
* (https://mutagen.readthedocs.io/en/latest/)
