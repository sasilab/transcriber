import streamlit as st
import requests
import zipfile
import os
import whisper  # OpenAI's Whisper model for transcription

import os
import requests
import zipfile

def download_ffmpeg():
    ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"  # URL for FFmpeg binaries
    ffmpeg_path = "/tmp/ffmpeg"  # Temporary path for FFmpeg on Streamlit Cloud

    if not os.path.exists(ffmpeg_path):
        os.makedirs(ffmpeg_path, exist_ok=True)
        
        # Download FFmpeg binaries
        print("Downloading FFmpeg binaries...")
        r = requests.get(ffmpeg_url)
        with open("ffmpeg.tar.xz", "wb") as f:
            f.write(r.content)
        
        # Extract the tar file (since it's tar.xz, not zip)
        print("Extracting FFmpeg binaries...")
        os.system(f"tar -xf ffmpeg.tar.xz -C {ffmpeg_path}")
        
        # Clean up
        os.remove("ffmpeg.tar.xz")
    
    # Add FFmpeg to the system path for the current session
    os.environ["PATH"] += os.pathsep + os.path.join(ffmpeg_path, 'ffmpeg-*/bin')  # Update path dynamically

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
