import os.path
import plistlib
import sys
import urllib
import urlparse

import Media


Virtual = True

LIB_FILENAME1 = "iTunes Library.xml"
LIB_FILENAME2 = "iTunes Music Library.xml"


def track_str(track, key):
    if key in track:
        return track[key].encode("utf-8")
    else:
        return None


def url2path(url):
    parsed_url = urlparse.urlparse(url)
    path = urllib.unquote(parsed_url.path)
    if sys.platform == "win32":  # Windows is speshul
        path = os.path.normpath(path[1:])  # "/C:/Path/To/File" -> "C:\Path\To\File"
    return path


def Scan(path, files, mediaList, subdirs, language=None, root=None):
    if not root:
        return

    # It would seem that the library file is called "iTunes Library.xml" on
    # Windows but "iTunes Music Library.xml" on OS X. Search up the folder
    # hierarchy from 'root' until we hit the root of the filesystem or find
    # either file.

    lib_folder = root
    while not os.path.exists(os.path.join(lib_folder, LIB_FILENAME1)) and \
            not os.path.exists(os.path.join(lib_folder, LIB_FILENAME2)):
        parent = os.path.dirname(lib_folder)
        if parent == lib_folder:
            raise Exception("Could not find iTunes library file")
        lib_folder = parent

    lib_path = os.path.join(lib_folder, LIB_FILENAME1)
    if not os.path.exists(lib_path):
        lib_path = os.path.join(lib_folder, LIB_FILENAME2)

    library = plistlib.readPlist(lib_path)

    song_kinds = {"AAC audio file", "MPEG audio file", "Apple Lossless audio file"}

    # The iTunes Library.xml on Windows doesn't appear to contain the
    # Music Folder entry, so let's assume the user selected the Music
    # folder as the root.

    if "Music Folder" in library:
        path_prefix = url2path(library["Music Folder"])
    else:
        path_prefix = root

    for track in library["Tracks"].values():
        if "Kind" not in track or track["Kind"] not in song_kinds:
            continue

        plex_track = Media.Track(
                artist=track_str(track, "Artist"),
                album=track_str(track, "Album"),
                title=track_str(track, "Name"),
                album_artist=track_str(track, "Album Artist"),
                index=track.get("Track Number", None),
                disc=track.get("Disc Number", 1),
                year=track.get("Year", None)
        )

        path = url2path(track_str(track, "Location"))

        if not path.startswith(path_prefix):
            # weird, this music file must live somewhere else so we can't access it
            continue

        plex_track.parts.append(path)

        mediaList.append(plex_track)
