import streamlit as st
import requests
import zipfile
import os
import whisper  # OpenAI's Whisper model for transcription

def download_ffmpeg():
    url = "https://drive.google.com/uc?export=download&id=1L0j4HqgKfLjYRnrsReNDwldmYbT_tBOt"  # Replace with your hosted FFmpeg binary link
    ffmpeg_path = "ffmpeg"
    if not os.path.exists(ffmpeg_path):
        os.makedirs(ffmpeg_path, exist_ok=True)
        st.info("Downloading FFmpeg binaries...")
        r = requests.get(url)
        with open("ffmpeg.zip", "wb") as f:
            f.write(r.content)
        with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
            zip_ref.extractall(ffmpeg_path)
        os.remove("ffmpeg.zip")
    os.environ["PATH"] += os.pathsep + os.path.abspath(ffmpeg_path)

def transcribe_audio(file_path):
    # Load Whisper model
    model = whisper.load_model("base")  # Change model type if needed (base, small, medium, large)
    result = model.transcribe(file_path)
    return result["text"]

# App setup
st.title("Audio/Video Transcription Service")
st.write("Upload your audio/video file and get a transcription!")

# Download FFmpeg at runtime
download_ffmpeg()

# File uploader
uploaded_file = st.file_uploader("Upload audio/video file", type=["mp3", "mp4", "wav", "m4a", "ogg", "mpeg4"])

if uploaded_file is not None:
    # Save uploaded file locally
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.info("Transcribing your file, please wait...")
    try:
        # Perform transcription
        transcription = transcribe_audio(file_path)
        st.success("Transcription completed!")
        st.text_area("Transcription:", transcription, height=300)
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
