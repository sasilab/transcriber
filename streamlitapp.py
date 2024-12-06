import streamlit as st
import requests
import zipfile
import os
import whisper  # OpenAI's Whisper model for transcription
import boto3
from botocore.exceptions import NoCredentialsError

# S3 Bucket information
BUCKET_NAME = 'sasmatic-s3-store1'
FFMPEG_FILE_KEY = 'ffmpeg.zip'

def download_ffmpeg_from_s3():
    """
    Downloads FFmpeg binaries from S3 and extracts them to a temporary location.
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )
    
    local_zip_path = '/tmp/ffmpeg.zip'
    ffmpeg_extract_path = '/tmp/ffmpeg/'

    try:
        # Download FFmpeg zip file from S3
        s3.download_file(BUCKET_NAME, FFMPEG_FILE_KEY, local_zip_path)
        st.info("FFmpeg downloaded successfully from S3.")

        # Ensure the extraction path exists
        os.makedirs(ffmpeg_extract_path, exist_ok=True)

        # Extract the zip file
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_extract_path)
        
        # Add FFmpeg to PATH
        os.environ["PATH"] += os.pathsep + ffmpeg_extract_path
        
        # Clean up
        os.remove(local_zip_path)
        st.info("FFmpeg successfully extracted and ready to use.")
    except NoCredentialsError:
        st.error("AWS credentials are not available. Check your Streamlit secrets configuration.")
    except Exception as e:
        st.error(f"An error occurred while downloading or extracting FFmpeg: {e}")

def transcribe_audio(file_path):
    """
    Transcribes audio using OpenAI Whisper.
    """
    try:
        # Load Whisper model
        model = whisper.load_model("base")  # Adjust model size as needed
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        raise RuntimeError(f"Error in transcription: {e}")

# Streamlit App
st.title("Audio/Video Transcription Service")
st.write("Upload your audio/video file and get a transcription!")

# Download FFmpeg at runtime
st.info("Setting up FFmpeg environment...")
download_ffmpeg_from_s3()

# File uploader
uploaded_file = st.file_uploader("Upload audio/video file", type=["mp3", "mp4", "wav", "m4a", "ogg", "mpeg4"])

if uploaded_file is not None:
    st.info("Processing your file...")
    try:
        # Save uploaded file locally
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        # Perform transcription
        st.info("Transcribing your file, please wait...")
        transcription = transcribe_audio(file_path)

        st.success("Transcription completed!")
        st.text_area("Transcription:", transcription, height=300)
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
