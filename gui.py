from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QTabWidget,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QFrame,
)

from PySide6.QtCore import (
    QThread,
    Signal,
)

from worker import DownloadWorker
from config import load_config, save_config


DARK_STYLESHEET = """
QWidget {
    background-color: #282828;
    color: #ebdbb2;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #282828;
}

/* Labels */

QLabel {
    background-color: transparent;
    color: #bdae93;
    border: none;
    padding: 0;
}

QLabel#appTitle {
    background-color: transparent;
    color: #ebdbb2;
    font-size: 29px;
    font-weight: 700;
}

QLabel#appSubtitle {
    background-color: transparent;
    color: #928374;
    font-size: 13px;
}

QLabel#fieldLabel {
    background-color: transparent;
    color: #a89984;
    border: none;
    padding: 0;
    margin: 0;
    font-size: 12px;
    font-weight: 600;
}

QLabel#statusLabel {
    background-color: transparent;
    color: #928374;
    border: none;
    padding: 4px 2px;
}

/* Cards */

QFrame#card {
    background-color: #3c3836;
    border: 1px solid #504945;
    border-radius: 10px;
}

QFrame#separator {
    background-color: #504945;
    min-height: 1px;
    max-height: 1px;
    border: none;
}

/* Inputs */

QLineEdit,
QComboBox,
QListWidget {
    background-color: #32302f;
    color: #ebdbb2;
    border: 1px solid #504945;
    border-radius: 7px;
    padding: 9px 10px;
    selection-background-color: #458588;
    selection-color: #fbf1c7;
}

QLineEdit:hover,
QComboBox:hover,
QListWidget:hover {
    border-color: #665c54;
}

QLineEdit:focus,
QComboBox:focus,
QListWidget:focus {
    border-color: #458588;
}

QLineEdit:disabled,
QComboBox:disabled,
QListWidget:disabled {
    background-color: #282828;
    color: #665c54;
    border-color: #3c3836;
}

QComboBox {
    padding-right: 30px;
}

QComboBox QAbstractItemView {
    background-color: #32302f;
    color: #ebdbb2;
    border: 1px solid #504945;
    selection-background-color: #458588;
    selection-color: #fbf1c7;
    padding: 4px;
}

/* Buttons */

QPushButton {
    background-color: #504945;
    color: #ebdbb2;
    border: 1px solid #665c54;
    border-radius: 7px;
    padding: 9px 16px;
    min-height: 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #665c54;
    border-color: #7c6f64;
}

QPushButton:pressed {
    background-color: #3c3836;
}

QPushButton:disabled {
    background-color: #32302f;
    color: #665c54;
    border-color: #3c3836;
}

QPushButton#primaryButton {
    background-color: #458588;
    color: #fbf1c7;
    border: 1px solid #689d6a;
}

QPushButton#primaryButton:hover {
    background-color: #689d6a;
    border-color: #8ec07c;
}

QPushButton#primaryButton:pressed {
    background-color: #3b6f70;
}

QPushButton#cancelButton {
    background-color: #3c2020;
    color: #fb4934;
    border-color: #cc241d;
}

QPushButton#cancelButton:hover {
    background-color: #4a2525;
    border-color: #fb4934;
}

/* Tabs */

QTabWidget {
    background-color: transparent;
}

QTabWidget::pane {
    background-color: transparent;
    border: none;
    padding: 0;
    margin: 0;
}

QTabBar {
    background-color: transparent;
    border: none;
}

QTabBar::tab {
    background-color: transparent;
    color: #928374;
    border: 1px solid transparent;
    border-bottom: 2px solid transparent;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 10px 18px 11px 18px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:hover {
    background-color: #3c3836;
    color: #d5c4a1;
}

QTabBar::tab:selected {
    background-color: #3c3836;
    color: #8ec07c;
    border-color: #504945;
    border-bottom-color: #8ec07c;
}

QTabBar::tab:disabled {
    color: #665c54;
}

/* Lists */

QListWidget {
    padding: 6px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 6px;
    margin: 2px;
}

QListWidget::item:hover {
    background-color: #504945;
}

QListWidget::item:selected {
    background-color: #458588;
    color: #fbf1c7;
}

/* Scrollbars */

QScrollBar:vertical {
    background: #282828;
    width: 9px;
    margin: 2px;
    border: none;
}

QScrollBar::handle:vertical {
    background: #504945;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #665c54;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

/* Status bar */

QStatusBar {
    background-color: #282828;
    color: #928374;
    border-top: 1px solid #3c3836;
    padding-left: 8px;
}
"""


def create_card():
    card = QFrame()
    card.setObjectName("card")
    return card


def create_field_label(text):
    label = QLabel(text)
    label.setObjectName("fieldLabel")
    return label


class SinglesTab(QWidget):
    download_state_changed = Signal(bool)
    queue_item_added = Signal(dict)

    def __init__(self, config):
        super().__init__()

        self.config = config

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Song title")

        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("Artist")

        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("Genre")

        self.album_input = QLineEdit()
        self.update_album_placeholder()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube URL")

        self.add_queue_button = QPushButton("Add to Queue")
        self.add_queue_button.clicked.connect(self.add_to_queue)

        self.download_button = QPushButton("Download")
        self.download_button.setObjectName("primaryButton")
        self.download_button.clicked.connect(self.start_download)

        self.cancel_button = QPushButton("Cancel Download")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_fields)

        card = create_card()

        form_layout = QGridLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(6)

        form_layout.addWidget(
            create_field_label("Title"),
            0,
            0,
        )

        form_layout.addWidget(
            self.title_input,
            1,
            0,
        )

        form_layout.addWidget(
            create_field_label("Artist"),
            0,
            1,
        )

        form_layout.addWidget(
            self.artist_input,
            1,
            1,
        )

        form_layout.addWidget(
            create_field_label("Genre"),
            2,
            0,
        )

        form_layout.addWidget(
            self.genre_input,
            3,
            0,
        )

        form_layout.addWidget(
            create_field_label("Album"),
            2,
            1,
        )

        form_layout.addWidget(
            self.album_input,
            3,
            1,
        )

        form_layout.addWidget(
            create_field_label("YouTube URL"),
            4,
            0,
            1,
            2,
        )

        form_layout.addWidget(
            self.url_input,
            5,
            0,
            1,
            2,
        )

        card.setLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(9)
        button_layout.addStretch()

        button_layout.addWidget(self.add_queue_button)

        button_layout.addWidget(self.download_button)

        button_layout.addWidget(self.cancel_button)

        button_layout.addWidget(self.clear_button)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(14)

        layout.addWidget(card)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setLayout(layout)

    def update_album_placeholder(self):
        self.album_input.setPlaceholderText(f"Default: {self.config['default_album']}")

    def clear_fields(self):
        self.title_input.clear()
        self.artist_input.clear()
        self.genre_input.clear()
        self.album_input.clear()
        self.url_input.clear()

    def add_to_queue(self):
        url = self.url_input.text().strip()
        title = self.title_input.text().strip()
        artist = self.artist_input.text().strip()
        genre = self.genre_input.text().strip()
        album = self.album_input.text().strip()

        if not url:
            self.status_label.setText("Enter a YouTube URL")
            return

        if not title:
            self.status_label.setText("Enter a song title")
            return

        if not artist:
            self.status_label.setText("Enter an artist")
            return

        item = {
            "type": "single",
            "url": url,
            "title": title,
            "artist": artist,
            "genre": genre,
            "album": album,
        }

        print("Adding single to queue:")
        print(item)

        self.queue_item_added.emit(item)

        self.status_label.setText("Added to queue")

        self.clear_fields()

    def start_download(self):
        url = self.url_input.text().strip()
        title = self.title_input.text().strip()
        artist = self.artist_input.text().strip()
        genre = self.genre_input.text().strip()
        album = self.album_input.text().strip()

        if not url:
            self.status_label.setText("Please enter a URL.")
            return

        if not title:
            self.status_label.setText("Please enter a title.")
            return

        if not artist:
            self.status_label.setText("Please enter an artist.")
            return

        self.set_download_state(True)

        self.thread = QThread()
        self.worker = DownloadWorker(
            self.config,
            "single",
            url=url,
            title=title,
            artist=artist,
            genre=genre,
            album=album,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.completed.connect(self.download_completed)
        self.worker.failed.connect(self.download_failed)
        self.worker.cancelled.connect(self.download_cancelled)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.set_download_state(False))

        self.thread.start()

    def cancel_download(self):
        if hasattr(self, "worker"):
            self.status_label.setText("Cancelling...")

            self.cancel_button.setEnabled(False)

            self.worker.cancel()

    def set_download_state(self, downloading):
        self.title_input.setEnabled(not downloading)

        self.artist_input.setEnabled(not downloading)

        self.genre_input.setEnabled(not downloading)

        self.album_input.setEnabled(not downloading)

        self.url_input.setEnabled(not downloading)

        self.add_queue_button.setEnabled(not downloading)

        self.download_button.setEnabled(not downloading)

        self.clear_button.setEnabled(not downloading)

        self.cancel_button.setEnabled(downloading)

        self.download_state_changed.emit(downloading)

    def download_completed(self, name):
        self.status_label.setText(f"{name} - Completed")

    def download_failed(self, error, name):
        self.status_label.setText(f"Download failed: {error}")

        print(f"Download failed: {error}")

    def download_cancelled(self):
        self.status_label.setText("Download cancelled")


class PlaylistTab(QWidget):
    download_state_changed = Signal(bool)
    queue_item_added = Signal(dict)

    def __init__(self, config):
        super().__init__()

        self.config = config

        self.album_input = QLineEdit()
        self.album_input.setPlaceholderText("Album")

        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("Artist")

        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("Genre")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube playlist URL")

        self.add_queue_button = QPushButton("Add to Queue")
        self.add_queue_button.clicked.connect(self.add_to_queue)

        self.download_button = QPushButton("Download")
        self.download_button.setObjectName("primaryButton")
        self.download_button.clicked.connect(self.start_download)

        self.cancel_button = QPushButton("Cancel Download")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_fields)

        card = create_card()

        form_layout = QGridLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(6)

        form_layout.addWidget(
            create_field_label("Album"),
            0,
            0,
        )

        form_layout.addWidget(
            self.album_input,
            1,
            0,
        )

        form_layout.addWidget(
            create_field_label("Artist"),
            0,
            1,
        )

        form_layout.addWidget(
            self.artist_input,
            1,
            1,
        )

        form_layout.addWidget(
            create_field_label("Genre"),
            2,
            0,
        )

        form_layout.addWidget(
            self.genre_input,
            3,
            0,
        )

        form_layout.addWidget(
            create_field_label("YouTube Playlist URL"),
            2,
            1,
        )

        form_layout.addWidget(
            self.url_input,
            3,
            1,
        )

        card.setLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(9)
        button_layout.addStretch()

        button_layout.addWidget(self.add_queue_button)

        button_layout.addWidget(self.download_button)

        button_layout.addWidget(self.cancel_button)

        button_layout.addWidget(self.clear_button)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(14)

        layout.addWidget(card)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setLayout(layout)

    def clear_fields(self):
        self.album_input.clear()
        self.artist_input.clear()
        self.genre_input.clear()
        self.url_input.clear()

    def add_to_queue(self):
        url = self.url_input.text().strip()
        album = self.album_input.text().strip()
        artist = self.artist_input.text().strip()
        genre = self.genre_input.text().strip()

        if not url:
            self.status_label.setText("Enter a YouTube playlist URL")
            return

        if not album:
            self.status_label.setText("Enter an album")
            return

        if not artist:
            self.status_label.setText("Enter an artist")
            return

        item = {
            "type": "playlist",
            "url": url,
            "artist": artist,
            "genre": genre,
            "album": album,
        }

        print("Adding playlist to queue:")
        print(item)

        self.queue_item_added.emit(item)

        self.status_label.setText("Added to queue")

        self.clear_fields()

    def start_download(self):
        url = self.url_input.text().strip()
        album = self.album_input.text().strip()
        artist = self.artist_input.text().strip()
        genre = self.genre_input.text().strip()

        if not url:
            self.status_label.setText("Enter a YouTube playlist URL")
            return

        if not album:
            self.status_label.setText("Enter an album")
            return

        if not artist:
            self.status_label.setText("Enter an artist")
            return

        self.set_download_state(True)

        self.status_label.setText("Downloading...")

        self.thread = QThread()

        self.worker = DownloadWorker(
            config=self.config,
            download_type="playlist",
            url=url,
            artist=artist,
            genre=genre,
            album=album,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.completed.connect(self.download_completed)

        self.worker.failed.connect(self.download_failed)

        self.worker.cancelled.connect(self.download_cancelled)

        self.worker.finished.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.finished.connect(lambda: self.set_download_state(False))

        self.thread.start()

    def cancel_download(self):
        if hasattr(self, "worker"):
            self.status_label.setText("Cancelling...")

            self.cancel_button.setEnabled(False)

            self.worker.cancel()

    def set_download_state(self, downloading):
        self.album_input.setEnabled(not downloading)

        self.artist_input.setEnabled(not downloading)

        self.genre_input.setEnabled(not downloading)

        self.url_input.setEnabled(not downloading)

        self.add_queue_button.setEnabled(not downloading)

        self.download_button.setEnabled(not downloading)

        self.clear_button.setEnabled(not downloading)

        self.cancel_button.setEnabled(downloading)

        self.download_state_changed.emit(downloading)

    def download_completed(self, name):
        self.status_label.setText(f"{name} - Completed")

    def download_failed(self, error, name):
        self.status_label.setText(f"Download failed: {error}")

        print(f"Download failed: {error}")

    def download_cancelled(self):
        self.status_label.setText("Download cancelled")


class SettingsTab(QWidget):
    settings_changed = Signal()

    def __init__(self, config):
        super().__init__()

        self.config = config

        self.save_location_input = QLineEdit()
        self.save_location_input.setText(self.config["save_location"])

        self.quality_input = QComboBox()

        self.quality_input.addItems(
            [
                "128",
                "192",
                "256",
                "320",
            ]
        )

        self.quality_input.setCurrentText(self.config["quality"])

        self.default_album_input = QLineEdit()
        self.default_album_input.setText(self.config["default_album"])

        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("primaryButton")

        self.save_button.clicked.connect(self.save_settings)

        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")

        card = create_card()

        form_layout = QGridLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(11)

        form_layout.addWidget(
            QLabel("Download Settings"),
            0,
            0,
            1,
            2,
        )

        form_layout.addWidget(
            create_field_label("Save Location"),
            1,
            0,
        )

        form_layout.addWidget(
            self.save_location_input,
            1,
            1,
        )

        form_layout.addWidget(
            create_field_label("Quality"),
            2,
            0,
        )

        form_layout.addWidget(
            self.quality_input,
            2,
            1,
        )

        form_layout.addWidget(
            create_field_label("Default Album"),
            3,
            0,
        )

        form_layout.addWidget(
            self.default_album_input,
            3,
            1,
        )

        card.setLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(14)

        layout.addWidget(card)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setLayout(layout)

    def save_settings(self):
        self.config["save_location"] = self.save_location_input.text()

        self.config["quality"] = self.quality_input.currentText()

        self.config["default_album"] = self.default_album_input.text()

        save_config(self.config)

        self.status_label.setText("Settings saved")

        self.settings_changed.emit()


class QueueTab(QWidget):
    queue_changed = Signal()

    def __init__(self, config):
        super().__init__()

        self.config = config
        self.queue = []

        self.queue_list = QListWidget()

        self.download_button = QPushButton("Download Queue")
        self.download_button.setObjectName("primaryButton")
        self.download_button.clicked.connect(self.start_queue)

        self.cancel_button = QPushButton("Cancel Queue")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel_queue)
        self.cancel_button.setEnabled(False)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected)

        self.clear_button = QPushButton("Clear Queue")
        self.clear_button.clicked.connect(self.clear_queue)

        self.status_label = QLabel("Queue is empty")
        self.status_label.setObjectName("statusLabel")

        card = create_card()

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)

        card_layout.addWidget(self.queue_list)

        card.setLayout(card_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(9)

        button_layout.addWidget(self.download_button)

        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        button_layout.addWidget(self.remove_button)

        button_layout.addWidget(self.clear_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(14)

        queue_title = QLabel("Queued Downloads")
        queue_title.setObjectName("sectionTitle")

        layout.addWidget(queue_title)

        layout.addWidget(card)

        layout.addLayout(button_layout)

        layout.addWidget(self.status_label)

        layout.addStretch()

        self.setLayout(layout)

    def add_item(self, item):
        clean_item = {
            "type": str(item.get("type", "")).strip(),
            "url": str(item.get("url", "")).strip(),
            "title": str(item.get("title", "")).strip(),
            "artist": str(item.get("artist", "")).strip(),
            "genre": str(item.get("genre", "")).strip(),
            "album": str(item.get("album", "")).strip(),
        }

        if not clean_item["url"]:
            self.status_label.setText("Cannot add item: URL is empty")
            return

        self.queue.append(clean_item)

        print("Queue now contains:")

        for queued_item in self.queue:
            print(queued_item)

        self.refresh_list()

        self.status_label.setText(f"{len(self.queue)} item(s) in queue")

        self.queue_changed.emit()

    def refresh_list(self):
        self.queue_list.clear()

        for index, item in enumerate(
            self.queue,
            start=1,
        ):
            if item["type"] == "single":
                name = f"{item['artist']} - {item['title']}"

                item_type = "Single"

            else:
                name = f"{item['artist']} - {item['album']}"

                item_type = "Playlist"

            display_text = f"{index}. [{item_type}] {name}"

            list_item = QListWidgetItem(display_text)

            self.queue_list.addItem(list_item)

    def remove_selected(self):
        if self.is_running():
            return

        selected_row = self.queue_list.currentRow()

        if selected_row < 0:
            return

        self.queue.pop(selected_row)

        self.refresh_list()
        self.update_status()

        self.queue_changed.emit()

    def clear_queue(self):
        if self.is_running():
            return

        self.queue.clear()

        self.refresh_list()
        self.update_status()

        self.queue_changed.emit()

    def update_status(self):
        count = len(self.queue)

        if count == 0:
            self.status_label.setText("Queue is empty")
        else:
            self.status_label.setText(f"{count} item(s) in queue")

    def is_running(self):
        return (
            hasattr(self, "worker")
            and hasattr(self, "thread")
            and self.thread.isRunning()
        )

    def start_queue(self):
        if not self.queue:
            self.status_label.setText("Queue is empty")
            return

        if self.is_running():
            return

        for index, item in enumerate(
            self.queue,
            start=1,
        ):
            if not item.get("url"):
                self.status_label.setText(f"Queue item {index} has an empty URL")
                return

        self.set_running_state(True)

        self.status_label.setText(f"Starting queue ({len(self.queue)} item(s))...")

        queue_copy = [dict(item) for item in self.queue]

        print("Starting queue with:")

        for item in queue_copy:
            print(item)

        self.thread = QThread()

        self.worker = DownloadWorker(
            config=self.config,
            download_type="queue",
            queue=queue_copy,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.item_completed.connect(self.item_completed)

        self.worker.item_failed.connect(self.item_failed)

        self.worker.completed.connect(self.queue_completed)

        self.worker.cancelled.connect(self.queue_cancelled)

        self.worker.finished.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.finished.connect(lambda: self.set_running_state(False))

        self.thread.start()

    def item_completed(self, name):
        self.status_label.setText(f"{name} - Completed")

    def item_failed(self, name, error):
        self.status_label.setText(f"{name} - Failed: {error}")

        print(f"Queue item failed: {name} - {error}")

    def queue_completed(self, message):
        self.status_label.setText(message)

        self.queue.clear()

        self.refresh_list()
        self.queue_changed.emit()

    def cancel_queue(self):
        if not self.is_running():
            return

        self.status_label.setText("Cancelling...")

        self.cancel_button.setEnabled(False)

        self.worker.cancel()

    def queue_cancelled(self):
        self.status_label.setText("Queue cancelled")

    def set_running_state(self, running):
        self.download_button.setEnabled(not running and bool(self.queue))

        self.cancel_button.setEnabled(running)

        self.remove_button.setEnabled(not running)

        self.clear_button.setEnabled(not running)

        self.queue_list.setEnabled(not running)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = load_config()

        self.setWindowTitle("TrackRip")

        self.resize(
            940,
            680,
        )

        self.tabs = QTabWidget()

        self.singles_tab = SinglesTab(self.config)

        self.playlist_tab = PlaylistTab(self.config)

        self.queue_tab = QueueTab(self.config)

        self.settings_tab = SettingsTab(self.config)

        self.tabs.addTab(self.singles_tab, "Singles")

        self.tabs.addTab(self.playlist_tab, "Playlist")

        self.tabs.addTab(self.queue_tab, "Queue")

        self.tabs.addTab(self.settings_tab, "Settings")

        self.singles_tab.queue_item_added.connect(self.queue_tab.add_item)

        self.playlist_tab.queue_item_added.connect(self.queue_tab.add_item)

        self.settings_tab.settings_changed.connect(
            self.singles_tab.update_album_placeholder
        )

        self.singles_tab.download_state_changed.connect(self.set_tabs_enabled)

        self.playlist_tab.download_state_changed.connect(self.set_tabs_enabled)

        self.queue_tab.queue_changed.connect(self.update_queue_state)

        central = QWidget()

        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(
            28,
            22,
            28,
            18,
        )
        central_layout.setSpacing(15)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(
            2,
            0,
            2,
            3,
        )
        header_layout.setSpacing(3)

        title = QLabel("TrackRip")
        title.setObjectName("appTitle")

        subtitle = QLabel("Download and manage your media library")
        subtitle.setObjectName("appSubtitle")

        header_layout.addWidget(title)

        header_layout.addWidget(subtitle)

        central_layout.addLayout(header_layout)

        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFixedHeight(1)

        central_layout.addWidget(separator)

        central_layout.addWidget(self.tabs)

        central.setLayout(central_layout)

        self.setCentralWidget(central)

        self.statusBar().showMessage("Ready")

        self.update_queue_state()

    def set_tabs_enabled(self, downloading):
        # The signal tells us whether a download is running.
        # Therefore tabs should be enabled only when it is NOT
        # downloading.
        self.tabs.tabBar().setEnabled(not downloading)

        if downloading:
            self.statusBar().showMessage("Downloading...")
        else:
            self.statusBar().showMessage("Ready")

    def update_queue_state(self):
        pass


def gui():
    app = QApplication([])

    app.setStyleSheet(DARK_STYLESHEET)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    gui()
