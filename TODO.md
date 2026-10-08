1. Project setup
- [x] Create a TrackRip 2.0 project directory and Git repository
- [x] Init uv and add yt-dlp and PySide6
- [x] Install FFmpeg and verify it is accessible from the terminal
- [x] Organise the code into separate GUI, downloader, and configuration modules

2. Refactor TrackRip 1.0
- [x] Move single-track downloading into a reusable downloader function
- [x] Move playlist downloading into a reusable downloader function
- [x] Keep configuration loading and saving in a separate module
- [x] Preserve MP3 conversion at 320 kbps and metadata tagging
- [x] Replace print-based progress reporting with callbacks or signals

3. Build the GUI
- [x] Create the main application window using PySide6
- [x] Add navigation or tabs for Single Track and Playlist modes
- [x] Add input fields for the URL, artist, genre, and album
- [x] Add a title field for single-track downloads
- [x] Add a Download button and a Cancel button

4. Connect the GUI to downloads
- [x] Run downloads in a QThread or worker so the GUI remains responsive
- [x] Display the current track and playlist download progress
- [x] Disable conflicting controls while a download is running
- [x] Implement safe cancellation and cleanup

5. Configuration and file management
- [x] Add settings tab
- [x] Load the saved download directory on startup
- [x] Allow users to change and save the default download directory
- [x] Allow users to change target quality and file type
- [x] Handle invalid filenames and special characters safely
- [x] Save configuration changes without corrupting the existing config

6. Testing
- [x] Test a single-track download
- [x] Test a multi-track playlist
- [x] Verify MP3 output and audio metadata
- [x] Test invalid URLs and unavailable videos
- [x] Test configuration persistence after restarting the app
- [x] Manually test cancellation and GUI responsiveness
- [x] Manually test end-to-end downloading 

7. Polish and release
- [x] Add a Queue feature
- [x] Improve layout, spacing, icons, and error messages
- [x] Write a README with installation and usage instructions
- [x] Package the application for distribution
