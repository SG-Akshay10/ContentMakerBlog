# # Content Creator Blog

"""
 This script creates a web-based application that converts a PDF document into a narrated video. Here's how it works:
 
 1. The user uploads a PDF file and a video file through a web interface.
 2. The application extracts text from the PDF.
 3. It generates an audio narration of the extracted text.
 4. The audio is then transcribed to create subtitles.
 5. Finally, the original video is combined with the generated audio and subtitles.
 
 The result is a video that plays the original content while narrating the text from the PDF with synchronized subtitles.

  Setup and Usage
 
 1. Ensure you have Python and pip installed on your system.
 2. Save this script as `pdf_to_video_narrator.py`.
 3. Create a `requirements.txt` file in the same directory with the following content:
 
    ```
    PyMuPDF
    numpy==1.23.5
    pandas
    gTTS
    openai-whisper
    pydub
    scikit-video
    SoundFile
    gradio
    ```
 
 4. Open a terminal in the directory containing these files and run:
 
    ```
    pip install -r requirements.txt
    ```
 
 5. Install FFmpeg separately, as it's required for video processing.
 6. Run the script:
 
    ```
    python pdf_to_video_narrator.py
    ```
 
 7. Open the provided URL in your web browser to access the interface.
 8. Upload a PDF and a video file, then wait for the processing to complete.
 9. Download or view the resulting narrated video.

  Code Explanation
 
 The script is organized into several sections, each handling a specific part of the process:
 
 1. PDF Text Extraction
 2. Audio Generation and Transcription
 3. Video Processing
 4. Main Processing Function
 5. Gradio Interface
 
 Each function is documented with its purpose, inputs, and outputs. The main processing logic is encapsulated in the `process_pdf_and_video()` function, which is called by the Gradio interface.
 
 Now, let's dive into the code:
"""
 ## Install dependencies

import warnings
warnings.filterwarnings("ignore")

import fitz
import numpy as np
import pandas as pd
import os
import re
from gtts import gTTS
import whisper
import tempfile
from pydub import AudioSegment
import skvideo.io
import soundfile as sf
from subprocess import check_output, STDOUT, CalledProcessError
import gradio as gr
import shutil
import traceback

# ## PDF Text Extraction

def pdf_extract(pdf_path):
    """
    Extracts all text from a PDF file.
    
    This function opens a PDF file, iterates through all its pages, and extracts the text content.
    It's useful for converting PDF documents into plain text for further processing.
    
    Args:
    pdf_path (str): The file path of the PDF from which to extract text.
    
    Returns:
    str: The extracted text from the PDF, with each page separated by a newline.
    """
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text() + "\n"
    doc.close()
    return text.strip()


def clean_text(text):
    """
    Cleans the extracted text by removing specific formats and correcting spacing.
    
    This function applies several regex-based cleaning operations to improve the quality of
    extracted text. It removes common artifacts from PDF extraction, such as escaped characters,
    author names, and unnecessary whitespace.
    
    Args:
    text (str): The text to be cleaned.
    
    Returns:
    str: The cleaned text, ready for further processing or narration.
    """
    # Replace escaped single quotes
    text = re.sub(r"(?i)\\\'", "'", text)
    
    # Remove authors' names and specific dataset names
    text = re.sub(r'\b[A-Z]+\s[A-Z]\s[A-Z]+(\s-\s[A-Z]\s-\s\d+)\b', '', text)
    
    # Remove section headings
    text = re.sub(r'\b\d+\.\s[A-Z]+\b', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text


def content_extract(file_name):
    """
    Extracts and cleans content from a PDF file.
    
    This function combines the PDF extraction and text cleaning steps into a single operation.
    It's the main entry point for processing PDF files in this application.
    
    Args:
    file_name (str): The name of the PDF file.
    
    Returns:
    str: The cleaned content of the PDF, ready for narration.
    """
    text = pdf_extract(file_name)
    text = clean_text(text)
    return text


# ## Audio Generation and Transcription

def generate_audio(text, language='en', filename='output.mp3'):
    """
    Generate audio from text using gTTS and save it to a file.
    
    This function converts the given text into speech using Google's Text-to-Speech (gTTS) service.
    It's used to create the narration audio for the video.
    
    Args:
    text (str): The text to convert to speech.
    language (str): The language of the text (default: 'en' for English).
    filename (str): The name of the output audio file (default: 'output.mp3').
    """
    tts = gTTS(text=text, lang=language)
    tts.save(filename)
    print(f"Audio saved as {filename}")


def convert_to_wav(mp3_filename):
    """
    Convert an MP3 file to WAV format for processing.
    
    This function is used because some audio processing libraries work better with WAV files.
    It converts the generated MP3 narration to WAV format for further processing.
    
    Args:
    mp3_filename (str): The name of the MP3 file.
    
    Returns:
    str: The name of the converted WAV file.
    """
    wav_filename = os.path.splitext(mp3_filename)[0] + '.wav'
    sound = AudioSegment.from_mp3(mp3_filename)
    sound.export(wav_filename, format="wav")
    return wav_filename


def transcribe_audio(audio_filename, model='small', output_dir='.', language='en'):
    """
    Transcribe audio file and generate subtitles.
    
    This function uses the Whisper model to transcribe the narration audio and generate subtitles.
    It's a key step in creating synchronized subtitles for the video.
    
    Args:
    audio_filename (str): The name of the audio file.
    model (str): The Whisper model to use (default: 'small').
    output_dir (str): The directory to save the output (default: '.').
    language (str): The language of the audio (default: 'en' for English).
    
    Returns:
    str: The path of the generated SRT subtitle file.
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_filename_wav = convert_to_wav(audio_filename)
    
    model = whisper.load_model(model)
    print(f"Transcribing {audio_filename}...")
    result = model.transcribe(audio_filename_wav, task='transcribe', language=language)
    
    srt_path = os.path.join(output_dir, os.path.splitext(os.path.basename(audio_filename))[0] + '.srt')
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        write_srt(iter(result['segments']), srt_file)
    
    os.remove(audio_filename_wav)  # Clean up the WAV file
    return srt_path


def write_srt(transcript, file):
    """
    Write the transcript to a file in SRT format.
    
    This function takes the transcription results and formats them into the SubRip (SRT) subtitle format.
    SRT is a widely supported format for video subtitles.
    
    Args:
    transcript (iterator): An iterator of transcript segments from the Whisper model.
    file (file object): The file to write the SRT content to.
    """
    for i, segment in enumerate(transcript, start=1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].replace('-->', '->').strip()
        file.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")


def format_timestamp(seconds):
    """
    Convert timestamp in seconds to SRT format.
    
    This helper function formats time in seconds to the HH:MM:SS,mmm format used in SRT files.
    
    Args:
    seconds (float): The timestamp in seconds.
    
    Returns:
    str: The formatted timestamp in SRT format (HH:MM:SS,mmm).
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"


# ## Video Processing

def overlay_audio_and_subtitles_on_video(video_path, audio_path, subtitle_path, output_path):
    """
    Overlay audio and subtitles on a video.
    
    This function combines the original video with the generated narration audio and subtitles.
    It uses FFmpeg to process the video, which allows for complex video manipulations.
    
    Args:
    video_path (str): Path to the input video file.
    audio_path (str): Path to the audio file (narration).
    subtitle_path (str): Path to the subtitle file (SRT format).
    output_path (str): Path for the output video file.
    """
    # Get video info
    video_info = skvideo.io.ffprobe(video_path)
    video_duration = float(video_info['video']['@duration'])
    
    # Read and adjust audio
    audio, sample_rate = sf.read(audio_path)
    audio_duration = len(audio) / sample_rate
    if audio_duration > video_duration:
        audio = audio[:int(video_duration * sample_rate)]
    elif audio_duration < video_duration:
        repeat_times = int(np.ceil(video_duration / audio_duration))
        audio = np.tile(audio, repeat_times)[:int(video_duration * sample_rate)]
    
    # Save adjusted audio
    temp_audio_path = 'temp_audio.wav'
    sf.write(temp_audio_path, audio, sample_rate)
    
    # Construct FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', temp_audio_path,
        '-vf', f"subtitles={subtitle_path}:force_style='FontName=Arial,Bold=10,FontSize=12,Alignment=6,MarginV=20'",
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_path
    ]
    
    # Execute FFmpeg command
    try:
        check_output(cmd, stderr=STDOUT)
        print(f"Video with overlaid audio and synchronized subtitles saved to {output_path}")
    except CalledProcessError as e:
        print(f"Error occurred: {e.output.decode()}")
    
    # Clean up temporary files
    os.remove(temp_audio_path)
    
    return output_path


# ## Main Processing Function


def process_pdf_and_video(pdf_file, video_file, output_filename):
    """
    Process a PDF file and a video file to create a narrated video.
    
    This function orchestrates the entire process of converting a PDF to a narrated video.
    It uses a 'data' folder for temporary files and cleans up afterwards.
    
    Args:
    pdf_file (str): Path to the PDF file.
    video_file (str): Path to the video file.
    
    Returns:
    str: Path to the output video file.
    """
    # Check if the file extensions are correct
    if not pdf_file.lower().endswith('.pdf'):
        raise ValueError("The provided PDF file does not have a .pdf extension.")
    if not video_file.lower().endswith('.mp4'):
        raise ValueError("The provided video file does not have a .mp4 extension.")
    
    # Create data folder if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Extract content from PDF
    content = content_extract(pdf_file)
    print("\nContent extracted from pdf file!!\n")
    
    # Generate audio from content
    audio_file = os.path.join('data', 'narration.mp3')
    generate_audio(content, filename=audio_file)
    print("\nAudio file generated!!!\n")
    
    # Transcribe audio to create subtitles
    subtitle_file = transcribe_audio(audio_file, output_dir='data')
    print("\nAudio transcription completed!!!\n")
    
    # Overlay audio and subtitles on video
    output_file = os.path.join('data', f'{output_filename}.mp4')
    overlay_audio_and_subtitles_on_video(video_file, audio_file, subtitle_file, output_file)
    print("\nVideo Output complete!!\n")
    
    # Move final output to current directory
    shutil.move(output_file, f'{output_filename}.mp4')
    
    # Clean up data folder
    for filename in os.listdir('data'):
        file_path = os.path.join('data', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    
    return f'{output_filename}.mp4'

# ## Create Gradio interface


def main(pdf_file, video_file, output_filename):
    try:
        output_video_path = process_pdf_and_video(pdf_file, video_file, output_filename)
        return output_video_path, ""  # Return video path and empty error
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        return None, error_message  # Return None for video and the error message

# Define the interface
iface = gr.Interface(
    fn=main,
    inputs=[
        gr.File(label="Upload a PDF"),
        gr.Video(label="Upload a Video"),
        gr.Text(label="Name of the Output File", placeholder="Enter the filename without extension")  
    ],
    outputs=[
        gr.Video(label="Processed Video"),
        gr.Textbox(label="Error Output")
    ],
    title="Video and PDF Processor",
    description="Upload a video and a PDF, and get the processed video."
)


# ## Launch the interface

if __name__ == "__main__":
    iface.launch()




