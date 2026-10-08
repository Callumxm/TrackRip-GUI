import glob
import os

from PySide6.QtCore import QObject, Signal, Slot

from downloader import (
    single_download,
    playlist_download,
    safe_filename,
)


class DownloadCancelled(Exception):
    pass


class DownloadWorker(QObject):
    completed = Signal(str)
    failed = Signal(str, str)
    cancelled = Signal()

    item_completed = Signal(str)
    item_failed = Signal(str, str)

    finished = Signal()

    def __init__(
        self,
        config,
        download_type,
        url=None,
        title=None,
        artist=None,
        genre=None,
        album=None,
        queue=None,
    ):
        super().__init__()

        self.config = config
        self.download_type = download_type

        self.url = url or ""
        self.title = title or ""
        self.artist = artist or ""
        self.genre = genre or ""
        self.album = album or ""

        self.queue = list(queue or [])

        self.cancel_requested = False

        self.current_item = None
        self.current_filename = None

    @Slot()
    def run(self):
        try:
            if self.download_type == "single":
                self.run_single()

            elif self.download_type == "playlist":
                self.run_playlist()

            elif self.download_type == "queue":
                self.run_queue()

            else:
                raise ValueError(
                    f"Unknown download type: "
                    f"{self.download_type}"
                )

        except DownloadCancelled:
            self.cleanup_current_download()
            self.cancelled.emit()

        except Exception as e:
            error_message = str(e).strip()

            if not error_message:
                error_message = (
                    "An unknown error occurred."
                )

            print("\nDownload failed:")
            print(error_message)

            if self.download_type == "queue":
                if self.current_item:
                    name = self.safe_item_name(
                        self.current_item
                    )

                    self.cleanup_current_download()

                    self.item_failed.emit(
                        name,
                        error_message,
                    )
                else:
                    self.item_failed.emit(
                        "Queue",
                        error_message,
                    )
            else:
                name = self.current_name()

                self.cleanup_current_download()

                self.failed.emit(
                    name,
                    error_message,
                )

        finally:
            # Always notify the GUI that the worker has
            # reached its terminal state.
            self.finished.emit()

    def run_single(self):
        self.current_item = {
            "type": "single",
            "url": self.url,
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
            "album": self.album,
        }

        self.validate_item(
            self.current_item
        )

        name = self.item_name(
            self.current_item
        )

        single_download(
            self.config,
            self.current_item["url"],
            self.current_item["title"],
            self.current_item["artist"],
            self.current_item["genre"],
            self.current_item["album"],
            self.progress_callback,
        )

        if self.cancel_requested:
            raise DownloadCancelled()

        self.current_filename = None

        self.item_completed.emit(name)
        self.completed.emit(name)

    def run_playlist(self):
        self.current_item = {
            "type": "playlist",
            "url": self.url,
            "artist": self.artist,
            "genre": self.genre,
            "album": self.album,
        }

        self.validate_item(
            self.current_item
        )

        name = self.item_name(
            self.current_item
        )

        playlist_download(
            self.config,
            self.current_item["url"],
            self.current_item["artist"],
            self.current_item["genre"],
            self.current_item["album"],
            self.progress_callback,
        )

        if self.cancel_requested:
            raise DownloadCancelled()

        self.current_filename = None

        self.item_completed.emit(name)
        self.completed.emit(name)

    def run_queue(self):
        total = len(self.queue)

        if total == 0:
            raise ValueError(
                "Queue is empty."
            )

        for index, original_item in enumerate(
            self.queue
        ):
            if self.cancel_requested:
                raise DownloadCancelled()

            item = dict(original_item)

            self.current_item = item
            self.current_filename = None

            name = self.safe_item_name(item)

            print(
                f"\nQueue item "
                f"{index + 1}/{total}: {name}"
            )

            try:
                self.validate_item(item)

                if item["type"] == "single":
                    single_download(
                        self.config,
                        item["url"],
                        item["title"],
                        item["artist"],
                        item["genre"],
                        item["album"],
                        self.progress_callback,
                    )

                elif item["type"] == "playlist":
                    playlist_download(
                        self.config,
                        item["url"],
                        item["artist"],
                        item["genre"],
                        item["album"],
                        self.progress_callback,
                    )

                else:
                    raise ValueError(
                        f"Unknown queue item type: "
                        f"{item.get('type')}"
                    )

                if self.cancel_requested:
                    raise DownloadCancelled()

                self.current_filename = None

                self.item_completed.emit(name)

            except DownloadCancelled:
                self.cleanup_current_download()
                raise

            except Exception as e:
                error_message = str(e).strip()

                if not error_message:
                    error_message = (
                        "An unknown error occurred."
                    )

                print(
                    f"\nQueue item failed: {name}"
                )
                print(error_message)

                self.cleanup_current_download()

                self.item_failed.emit(
                    name,
                    error_message,
                )

                continue

            finally:
                self.current_filename = None

        self.completed.emit(
            f"Queue completed - "
            f"{total} item(s)"
        )

    def validate_item(self, item):
        item_type = item.get("type")

        url = str(
            item.get("url", "")
        ).strip()

        if not url:
            raise ValueError(
                "Queue item has an empty URL."
            )

        if item_type == "single":
            if not str(
                item.get("title", "")
            ).strip():
                raise ValueError(
                    "Queue item has no song title."
                )

            if not str(
                item.get("artist", "")
            ).strip():
                raise ValueError(
                    "Queue item has no artist."
                )

        elif item_type == "playlist":
            if not str(
                item.get("album", "")
            ).strip():
                raise ValueError(
                    "Queue item has no album."
                )

            if not str(
                item.get("artist", "")
            ).strip():
                raise ValueError(
                    "Queue item has no artist."
                )

        else:
            raise ValueError(
                f"Invalid queue item type: "
                f"{item_type}"
            )

    def item_name(self, item):
        if item["type"] == "single":
            return (
                f"{item['artist']} - "
                f"{item['title']}"
            )

        return (
            f"{item['artist']} - "
            f"{item['album']}"
        )

    def safe_item_name(self, item):
        try:
            return self.item_name(item)
        except (KeyError, TypeError):
            return "Download"

    def current_name(self):
        if self.current_item:
            return self.safe_item_name(
                self.current_item
            )

        return "Download"

    def progress_callback(self, data):
        filename = data.get("filename")

        if filename:
            self.current_filename = filename

        if self.cancel_requested:
            raise DownloadCancelled()

    @Slot()
    def cancel(self):
        self.cancel_requested = True

    def cleanup_current_download(self):
        if not self.current_item:
            return

        if self.current_filename:
            self.remove_file_variants(
                self.current_filename
            )

        item_type = self.current_item.get(
            "type"
        )

        if item_type == "single":
            self.cleanup_single()

        elif item_type == "playlist":
            self.cleanup_playlist_current_file()

    def cleanup_single(self):
        item = self.current_item

        album = safe_filename(
            item.get("album")
            or self.config["default_album"]
        )

        artist = safe_filename(
            item.get("artist", "")
        )

        title = safe_filename(
            item.get("title", "")
        )

        save_location = os.path.expanduser(
            self.config["save_location"]
        )

        album_folder = os.path.join(
            save_location,
            album,
        )

        filename_base = (
            f"{artist} - {title}"
        )

        patterns = [
            f"{filename_base}.mp3",
            f"{filename_base}.*.part",
            f"{filename_base}.*.ytdl",
            f"{filename_base}.*.part-Frag*",
            f"{filename_base}.part",
            f"{filename_base}.ytdl",
        ]

        self.remove_patterns(
            album_folder,
            patterns,
            remove_final_mp3=True,
        )

    def cleanup_playlist_current_file(self):
        if self.current_filename:
            self.remove_file_variants(
                self.current_filename
            )

    def remove_file_variants(
        self,
        filename,
        remove_final_mp3=True,
    ):
        if not filename:
            return

        candidates = set()

        candidates.add(filename)
        candidates.add(
            f"{filename}.part"
        )
        candidates.add(
            f"{filename}.ytdl"
        )

        candidates.update(
            glob.glob(
                f"{filename}.part-Frag*"
            )
        )

        root, extension = os.path.splitext(
            filename
        )

        if extension.lower() != ".mp3":
            candidates.add(
                f"{root}.mp3"
            )

        if not remove_final_mp3:
            candidates = {
                candidate
                for candidate in candidates
                if not candidate.lower().endswith(
                    ".mp3"
                )
            }

        for candidate in candidates:
            self.remove_file(candidate)

    def remove_patterns(
        self,
        folder,
        patterns,
        remove_final_mp3=True,
    ):
        if not os.path.exists(folder):
            return

        for pattern in patterns:
            matches = glob.glob(
                os.path.join(
                    folder,
                    pattern,
                )
            )

            for filename in matches:
                if (
                    not remove_final_mp3
                    and filename.lower().endswith(
                        ".mp3"
                    )
                ):
                    continue

                self.remove_file(filename)

    def remove_file(self, filename):
        try:
            if os.path.isfile(filename):
                os.remove(filename)

                print(
                    f"Cancelled temporary file removed: "
                    f"{filename}"
                )

        except OSError as e:
            print(
                f"Could not remove cancelled file "
                f"{filename}: {e}"
            )
