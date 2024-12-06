import streamlit as st
import requests
import zipfile
import os
import whisper  # OpenAI's Whisper model for transcription
import boto3
from botocore.exceptions import NoCredentialsError

# S3 Bucket information
BUCKET_NAME = 'sasmatic-s3-store1'
FFMPEG_FILE_KEY = 'ffmpeg/ffmpeg.tar.xz'

def download_ffmpeg_from_s3():
    s3 = boto3.client('s3')
    local_filename = '/tmp/ffmpeg.tar.xz'
    
    try:
        s3.download_file(BUCKET_NAME, FFMPEG_FILE_KEY, local_filename)
        print("FFmpeg downloaded successfully.")
        # You can extract it if it's a tar file, for example
        os.system(f"tar -xf {local_filename} -C /tmp/ffmpeg/")
        os.remove(local_filename)
    except NoCredentialsError:
        print("Credentials not available")

# Call the function to download FFmpeg
download_ffmpeg_from_s3()


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
