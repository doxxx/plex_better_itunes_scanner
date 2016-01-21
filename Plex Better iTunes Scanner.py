import os.path
import plistlib
import sys
import urllib
import urlparse

import Media


Virtual = True


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

    library = plistlib.readPlist(root + "/iTunes Music Library.xml")

    song_kinds = {"AAC audio file", "MPEG audio file", "Apple Lossless audio file"}

    path_prefix = urllib.unquote(urlparse.urlparse(library["Music Folder"]).path)

    for track in library["Tracks"].values():
        if track["Kind"] not in song_kinds:
            continue

        plex_track = Media.Track(
                artist=track_str(track, "Artist"),
                album=track_str(track, "Album"),
                title=track_str(track, "Name"),
                album_artist=track_str(track, "Album Artist"),
                index=track.get("Track Number", None),
                disc=track.get("Disc Number", 1),
        )

        path = url2path(track_str(track, "Location"))

        if not path.startswith(path_prefix):
            # weird, this music file must live somewhere else so we can't access it
            continue

        plex_track.parts.append(path)

        mediaList.append(plex_track)
