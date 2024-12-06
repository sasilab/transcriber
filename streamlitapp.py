import os
import subprocess
import streamlit as st
import whisper


# Check if FFmpeg is installed
def check_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except FileNotFoundError:
        return False


# Verify FFmpeg
if not check_ffmpeg_installed():
    st.error("FFmpeg is not installed or not accessible. Please install FFmpeg to proceed.")
else:
    # Load the Whisper model
    @st.cache_resource
    def load_model():
        return whisper.load_model("base")


    model = load_model()

    # Streamlit UI
    st.title("Audio/Video Transcription Service")
    st.write("Upload your audio/video file and get a transcription!")

    uploaded_file = st.file_uploader("Upload a file", type=["mp3", "mp4", "wav", "m4a", "ogg", "mpeg4"])

    if uploaded_file is not None:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.write(f"File uploaded: {uploaded_file.name}")

        try:
            with st.spinner("Transcribing..."):
                result = model.transcribe(file_path)
                transcription = result["text"]

            st.subheader("Transcription")
            st.text_area("Transcribed Text", transcription, height=300)

            st.download_button(
                label="Download Transcription",
                data=transcription,
                file_name="transcription.txt",
                mime="text/plain",
            )
        except Exception as e:
            st.error(f"An error occurred during transcription: {e}")
