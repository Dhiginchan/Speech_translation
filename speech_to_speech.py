import os
import ffmpeg
import speech_recognition as sr
from pydub import AudioSegment
from deep_translator import GoogleTranslator
from gtts import gTTS

# File paths
INPUT_VIDEO = r"C:\Users\dhigi\OneDrive\Desktop\GEN AI\input_video3.mp4"
EXTRACTED_AUDIO_MP3 = "extracted_audio.mp3"
EXTRACTED_AUDIO_WAV = "extracted_audio.wav"
TEXT_FILE = "transcribed_text.txt"
TRANSLATED_TEXT_FILE = "translated_text.txt"
TRANSLATED_AUDIO = "translated_audio.mp3"
FINAL_VIDEO = "final_video.mp4"

# Step 1: Get user input for target language
def get_user_language_choice():
    print("🔹 Available Languages:")
    print("1. Arabic (ar)")
    print("2. Bengali (bn)")
    print("3. Chinese (zh)")
    print("4. French (fr)")
    print("5. German (de)")
    print("6. Hindi (hi)")
    print("7. Italian (it)")
    print("8. Japanese (ja)")
    print("9. Kannada (kn)")
    print("10. Malayalam (ml)")
    print("11. Marathi (mr)")
    print("12. Punjabi (pa)")
    print("13. Spanish (es)")
    print("14. Tamil (ta)")
    print("15. Telugu (te)")

    language_code = input("Enter the language code of your choice (e.g., 'ta' for Tamil): ").strip()
    return language_code

# Get the target language from user input
TARGET_LANGUAGE = get_user_language_choice()

# Step 2: Extract Audio from Video
def extract_audio():
    print("🔹 Extracting audio from video...")
    try:
        if not os.path.exists(INPUT_VIDEO):
            print(f"❌ Error: Video file '{INPUT_VIDEO}' not found.")
            return

        ffmpeg.input(INPUT_VIDEO).output(EXTRACTED_AUDIO_MP3, format='mp3', acodec='libmp3lame').run(overwrite_output=True, quiet=True)

        if os.path.exists(EXTRACTED_AUDIO_MP3):
            print("✅ Audio extracted successfully.")
        else:
            print("❌ Error: Audio extraction failed.")
    except Exception as e:
        print(f"❌ Error extracting audio: {e}")

# Step 3: Convert MP3 to WAV
def convert_mp3_to_wav():
    print("🔹 Converting MP3 to WAV format...")
    try:
        if not os.path.exists(EXTRACTED_AUDIO_MP3):
            print(f"❌ Error: MP3 file '{EXTRACTED_AUDIO_MP3}' not found.")
            return
        
        audio = AudioSegment.from_mp3(EXTRACTED_AUDIO_MP3)
        audio.export(EXTRACTED_AUDIO_WAV, format="wav")
        print("✅ Conversion to WAV completed.")
    except Exception as e:
        print(f"❌ Error converting MP3 to WAV: {e}")

# Step 4: Convert Audio to Text
def audio_to_text():
    print("🔹 Converting audio to text using Google Speech Recognition...")
    try:
        if not os.path.exists(EXTRACTED_AUDIO_WAV):
            print(f"❌ Error: WAV file '{EXTRACTED_AUDIO_WAV}' not found.")
            return ""

        recognizer = sr.Recognizer()
        with sr.AudioFile(EXTRACTED_AUDIO_WAV) as source:
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data)

        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(text)

        print("✅ Text transcription completed.")
        return text
    except sr.UnknownValueError:
        print("❌ Google Speech Recognition could not understand the audio.")
        return ""
    except sr.RequestError:
        print("❌ Could not request results from Google Speech Recognition.")
        return ""
    except Exception as e:
        print(f"❌ Error in speech recognition: {e}")
        return ""

# Step 5: Translate Text
def translate_text():
    print(f"🔹 Translating text to {TARGET_LANGUAGE}...")
    try:
        if not os.path.exists(TEXT_FILE):
            print(f"❌ Error: Transcribed text file '{TEXT_FILE}' not found.")
            return ""

        with open(TEXT_FILE, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            print("❌ Error: No text found to translate.")
            return ""

        translated_text = GoogleTranslator(source='auto', target=TARGET_LANGUAGE).translate(text)

        with open(TRANSLATED_TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(translated_text)

        print("✅ Translation completed.")
        return translated_text
    except Exception as e:
        print(f"❌ Error translating text: {e}")
        return ""

# Step 6: Convert Translated Text to Speech
def text_to_speech():
    print("🔹 Converting translated text to speech...")
    try:
        if not os.path.exists(TRANSLATED_TEXT_FILE):
            print(f"❌ Error: Translated text file '{TRANSLATED_TEXT_FILE}' not found.")
            return

        with open(TRANSLATED_TEXT_FILE, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            print("❌ Error: No translated text found to convert to speech.")
            return

        tts = gTTS(text=text, lang=TARGET_LANGUAGE)
        tts.save(TRANSLATED_AUDIO)
        print(f"✅ Audio translation completed. Saved as '{TRANSLATED_AUDIO}'.")
    except Exception as e:
        print(f"❌ Error converting text to speech: {e}")

# Step 7: Merge Translated Audio with Video
def merge_audio_with_video():
    print("🔹 Merging translated audio with video...")

    try:
        if not os.path.exists(INPUT_VIDEO):
            print(f"❌ Error: Video file '{INPUT_VIDEO}' not found.")
            return

        if not os.path.exists(TRANSLATED_AUDIO):
            print(f"❌ Error: Translated audio file '{TRANSLATED_AUDIO}' not found.")
            return

        video_without_audio = "video_no_audio.mp4"
        ffmpeg.input(INPUT_VIDEO).output(video_without_audio, an=None, vcodec='copy').run(overwrite_output=True, quiet=True)

        video_duration = float(ffmpeg.probe(INPUT_VIDEO)["format"]["duration"])
        audio = AudioSegment.from_file(TRANSLATED_AUDIO)
        audio_duration = len(audio) / 1000.0  # Convert ms to seconds

        if audio_duration < video_duration:
            silence = AudioSegment.silent(duration=(video_duration - audio_duration) * 1000)
            final_audio = audio + silence
        else:
            final_audio = audio[:int(video_duration * 1000)]

        # Save adjusted audio
        final_audio.export(TRANSLATED_AUDIO, format="mp3")

        # ✅ FIX: Use ffmpeg.output() correctly
        video = ffmpeg.input(video_without_audio)
        audio = ffmpeg.input(TRANSLATED_AUDIO)
        ffmpeg.output(video, audio, FINAL_VIDEO, vcodec='copy', acodec='aac').run(overwrite_output=True, quiet=True)

        if os.path.exists(FINAL_VIDEO):
            print(f"✅ Final translated video saved as '{FINAL_VIDEO}'.")
        else:
            print("❌ Error: Final video was not created.")

    except Exception as e:
        print(f"❌ Error merging audio with video: {e}")

# Run all steps
extract_audio()  
convert_mp3_to_wav()  
transcribed_text = audio_to_text()
translated_text = translate_text()
text_to_speech()
merge_audio_with_video()
