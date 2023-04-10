import argparse
import io
import os
import speech_recognition as sr
import whisper
import torch
import pinecone
import openai

from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from collections import Counter, defaultdict
import re

from genius_get_song import search_song



def returns_max(list):
    try:
        counter = Counter(list)
        most_common_element = counter.most_common(1)[0][0]
        print("Most common element:", most_common_element)
        return most_common_element.strip()
    except:
        return list[0]

def clean_transcription(text):
    # Remove extra whitespace and special characters
    text = re.sub(r'\W+', ' ', text)
    return text.strip()

def get_most_common_words(transcription, n=5):
    word_count = defaultdict(int)
    for line in transcription:
        words = line.split()
        for word in words:
            word_count[word.lower()] += 1
    return sorted(word_count, key=word_count.get, reverse=True)[:n]
def live_speech_rec():

    """
    Records lyrics untill current top song matches an overall

    :return:
    """
    model = 'tiny.en'
    args = argparse.Namespace(
        model=model,
        energy_threshold=1500,  # Increased from 1000
        record_timeout=4,  # Increased from 2
        phrase_timeout=5  # Increased from 3
    )

    phrase_time = None
    last_sample = bytes()
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False

    source = sr.Microphone(sample_rate=16000)

    audio_model = whisper.load_model(args.model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    temp_file = NamedTemporaryFile().name
    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)


    total_songs = []
    total_artists = []
    print("{0} loaded.\n".format(model))
    checker = 0
    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                phrase_time = now

                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                with open(temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                os.system('cls' if os.name == 'nt' else 'clear')
                checker += 1
                for i, line in enumerate(transcription):
                    print(i, line)
                    # After 3 lines (reduced from 10), try again
                    if i > 3:
                        transcription = []

                try:
                    print(transcription[-1])
                except:
                    print("")

                try:
                    single, artist, confidence = search_song(transcription[-1])
                except:
                    pass


                # total, artist = search_song(transcription)
                total_songs.append(single)
                total_artists.append(artist)
                # total_songs.append(total)

                try:
                    if confidence > 0.8 and checker > 3:  # Confidence threshold added
                        print(total_songs)
                        return returns_max(total_songs), returns_max(total_artists)
                except:
                    pass
                print('', end='', flush=True)

                sleep(0.15)
        except KeyboardInterrupt:
            break


    print("\n\nTranscription:")
    for i, line in enumerate(transcription):
        if i != 0:
            print(i, line)



if __name__ == "__main__":

    # High confidience this is the correct song title
    song_title = live_speech_rec()
