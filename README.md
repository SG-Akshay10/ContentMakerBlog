# Content Maker Blog 

This project is a Python-based web application that transforms a PDF document into a narrated video with synchronized subtitles. It automates the process of converting text-based content into engaging video material, making it easier to create multimedia content from your documents.

## Features

  * **`PDF Text Extraction`**: Automatically extracts text from a PDF document.
  * **`Text-to-Speech (TTS)`**: Converts extracted text into an audio narration using Google's Text-to-Speech (gTTS) service.
  * **`Audio Transcription`**: Uses the Whisper model to transcribe the generated audio into subtitles in SRT format.
  * **`Video Processing`**: Overlays the audio narration and subtitles onto a provided video file.
  * **`User-Friendly Interface`**: A web interface built with Gradio allows users to upload files, start the processing, and download the resulting video.

## How It Works

  * **`Upload Files`**: Users upload a PDF file and a video file through the Gradio web interface.
  * **`Text Extraction`**: The application extracts text from the PDF.
  * **`Audio Generation`**: The extracted text is converted into an audio narration.
  * **`Subtitle Creation`**: The audio is transcribed into subtitles.
  * **`Video Overlay`**: The narration and subtitles are overlaid onto the original video.
  * **`Download`**: The final narrated video with synchronized subtitles is available for download.

## Installation
### Prerequisites

* Python 3.x
* FFmpeg (required for video processing)

### Setup

1. Clone the Repository:

```
git clone https://github.com/yourusername/content-creator-blog.git
cd content-creator-blog
```

2. Install Dependencies: Make sure you have pip installed. Then run:
```
pip install -r requirements.txt
```

3. Install FFmpeg: Follow the instructions to install FFmpeg for your operating system from [FFmpeg.org](https://www.ffmpeg.org/).

### Usage

1. Run the Application: In the terminal, navigate to the project directory and execute the script:
    ```
    python pdf_to_video_narrator.py
    ```
2. Access the Web Interface: After running the script, Gradio will launch a web interface. Open the provided URL in your web browser.

3. Upload Files:
    * PDF File: Upload the PDF document you wish to convert.
    * Video File: Upload the video file where the narration and subtitles will be overlaid.
    * Output Filename: Provide the desired name for the output file (without extension).

4. Process: Click the "Submit" button and wait for the processing to complete. The interface will display the final video, which you can download or preview directly.

### Code Overview

The script is divided into several key sections:

* PDF Text Extraction: Extracts and cleans text from the uploaded PDF file.
* Audio Generation: Converts the cleaned text into an audio file using gTTS.
* Audio Transcription: Transcribes the audio into subtitles using the Whisper model.
* Video Processing: Overlays the generated audio and subtitles onto the uploaded video.
* Gradio Interface: Provides a web-based interface for file upload and processing.

Main Functions

* `pdf_extract(pdf_path)`: Extracts text from the PDF file.
* `clean_text(text)`: Cleans the extracted text by removing unwanted characters and formatting.
* `generate_audio(text, language='en', filename='output.mp3')`: Converts text into speech and saves it as an audio file.
* `transcribe_audio(audio_filename, model='small', output_dir='.', language='en')`: Transcribes audio to create subtitles.
* `overlay_audio_and_subtitles_on_video(video_path, audio_path, subtitle_path, output_path)`: Overlays audio and subtitles onto the video.
* `process_pdf_and_video(pdf_file, video_file, output_filename)`: Orchestrates the entire process from PDF extraction to video creation.

## Example

Here's a quick example to demonstrate how the project works:

1. Run the script
  
```
python pdf_to_video_narrator.py
```

2. Open the URL provided by Gradio in your browser.

3. Upload a PDF document and a video file.

4. Provide the desired output filename.

5. Wait for the processing to complete and download your video.

## Working Screenshot and Video

![Screenshot from 2024-09-01 21-23-47](https://github.com/user-attachments/assets/2828cb04-389a-48c4-be1b-1fb034208a14)

![Screenshot from 2024-09-01 21-24-18](https://github.com/user-attachments/assets/9091d65e-e148-4104-82a3-93ee76284135)

## Click here to check the [How to use tutorials](https://drive.google.com/file/d/1Ku-jjZBnaLOWhl1A_k-FSQlvN76M1cYa/view?usp=sharing)
## Click here to check the [Output](https://drive.google.com/file/d/10_PwiMDn5_rGblZR_SYbmHEamEubj3v0/view?usp=sharing)

This project is licensed under the MIT License. See the LICENSE file for more details.
