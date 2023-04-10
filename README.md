# TextAndAudio_SongFinder

This project aims to provide song recommendations based on the lyrics and features of the current song the user is listening to. Users can either type or sing the lyrics they remember, and the project will suggest songs with similar lyrical content and musical features.

Credit to @https://github.com/davabase/whisper_real_time for the base realtime audo software -> was adapted to be better at picking out song lyrics.

## Getting Started

### Prerequisites

- Python 3.10

### Installation

1. Clone the repository:
git clone https://github.com/AJclemendor/TextAndAudio_SongFinder.git


2. Navigate to the project directory:
cd SemanticSongRecommendations


3. Install the required packages:
pip install -r requirements.txt


### Usage

1. To run the project, execute the following command:
python src/reccomend_song-runner.py

2. When prompted, choose whether to type (1) or sing (2) the lyrics.

3. Follow the on-screen instructions to get song recommendations.

## File Structure

- `src/reccomend_song-runner.py`: The main script to run the project.
- `src/find_song_live_audio.py`: Handles the live speech recognition and searches for the song based on the recognized lyrics.
- `src/lyricsgenius.py`: A wrapper for the Genius API to search for song lyrics.
- `src/create_local_db.py`: Creates a local database of songs and genres.

## Built With

- Python 3.10
- [LyricsGenius](https://github.com/johnwmillr/LyricsGenius): A simple Python wrapper for the Genius API.
- [SpeechRecognition](https://github.com/Uberi/speech_recognition): A Python library for performing speech recognition with support for multiple engines and APIs.
- [Whisper](https://github.com/RuABraun/whisper): A deep learning-based speech recognition library for Python.
- [Spotipy](https://github.com/plamere/spotipy): A lightweight Python library for the Spotify Web API.

## Author

- ajcle




