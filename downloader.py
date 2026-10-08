import os
import re

from yt_dlp import YoutubeDL


def safe_filename(value):
    value = str(value).strip()

    # Remove characters that are invalid or problematic
    # in filenames.
    value = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        value,
    )

    # Remove control characters.
    value = re.sub(
        r"[\x00-\x1f]",
        "",
        value,
    )

    # Prevent filenames ending with spaces or periods.
    value = value.rstrip(" .")

    # Prevent Windows reserved device names.
    if value.upper() in {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }:
        value = f"_{value}"

    # Avoid empty filenames.
    return value or "Unknown"


def single_download(
    config,
    url,
    title,
    artist,
    genre,
    album,
    progress_callback=None,
):
    if not album:
        album = config["default_album"]

    title = safe_filename(title)
    artist = safe_filename(artist)
    genre = safe_filename(genre)
    album = safe_filename(album)

    # Check that the URL points to a single video,
    # not a playlist.
    with YoutubeDL(
        {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
        }
    ) as ydl:
        info = ydl.extract_info(
            url,
            download=False,
        )

    if info.get("_type") == "playlist":
        raise ValueError(
            "Playlist URL cannot be used in the Singles tab."
        )

    save_path = os.path.expanduser(
        f"{config['save_location']}/{album}"
    )

    os.makedirs(
        save_path,
        exist_ok=True,
    )

    dl_opts = create_download_options(
        f"{save_path}/{artist} - {title}.%(ext)s",
        {
            "title": title,
            "artist": artist,
            "genre": genre,
            "album": album,
        },
        config,
        progress_callback,
    )

    with YoutubeDL(dl_opts) as ydl:
        ydl.download([url])


def playlist_download(
    config,
    url,
    artist,
    genre,
    album,
    progress_callback=None,
):
    if not album:
        album = config["default_album"]

    artist = safe_filename(artist)
    genre = safe_filename(genre)
    album = safe_filename(album)

    # Check that the URL is a playlist.
    with YoutubeDL(
        {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "ignoreerrors": True,
        }
    ) as ydl:
        info = ydl.extract_info(
            url,
            download=False,
        )

    if not info:
        raise ValueError(
            "Could not extract playlist information."
        )

    if info.get("_type") != "playlist":
        raise ValueError(
            "Single video URL cannot be used in the Playlist tab."
        )

    save_path = os.path.expanduser(
        f"{config['save_location']}/{album}"
    )

    os.makedirs(
        save_path,
        exist_ok=True,
    )

    dl_opts = create_download_options(
        f"{save_path}/{artist} - %(title)s.%(ext)s",
        {
            "artist": artist,
            "genre": genre,
            "album": album,
        },
        config,
        progress_callback,
        ignore_errors=True,
    )

    with YoutubeDL(dl_opts) as ydl:
        ydl.download([url])


def create_download_options(
    output_template,
    metadata,
    config,
    progress_callback=None,
    ignore_errors=False,
):
    return {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "ignoreerrors": ignore_errors,
        "progress_hooks": (
            [progress_callback]
            if progress_callback
            else []
        ),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": config["quality"],
            },
            {
                "key": "FFmpegMetadata",
            },
        ],
        "postprocessor_args": [
            item
            for key, value in metadata.items()
            for item in (
                "-metadata",
                f"{key}={value}",
            )
        ],
    }


def progress_hook(data, progress_callback=None):
    if progress_callback:
        progress_callback(data)
