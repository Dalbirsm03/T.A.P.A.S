import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


general_model = genai.GenerativeModel('gemini-1.5-pro')
code_model = genai.GenerativeModel('gemini-1.5-flash')

# Function to transcribe audio
def run_genai_logic_audio(audio_file):
    my_audio_file = genai.upload_file(path=audio_file)
    
    while my_audio_file.state.name == "PROCESSING":
        time.sleep(5)
        my_audio_file = genai.get_file(my_audio_file.name)
    
    prompt = "Understand the audio and convert the audio into text."
    response = general_model.generate_content([my_audio_file, prompt])
    return response.text

def decide(transcribed_text):
    prompt = f"""Analyze the following text: "{transcribed_text}".
    Classify the problem as one of the following:
    - code_error: If the problem is related to code errors or exceptions.
    - other: If the problem is related to general inquiries, file paths, user errors, or other non-technical matters.
    Provide only the classification as your response, ensuring it accurately reflects the core issue described in the text."""
    
    response = general_model.generate_content(prompt)
    
    problem_type = response.text.replace("*", "").strip().lower()
    print(problem_type)
    return problem_type

def route_based_on_classification(transcribed_text, video_file):
    task_type = decide(transcribed_text)
    
    if task_type == "code_error":
        prompt = f"""Generate the correct version of the code by carefully analyzing the {video_file} and {transcribed_text}, and provide only the correct code without any explanations"""
        model = code_model
    
    else:
        prompt = f"""The following text '{transcribed_text}' outlines an issue related to '{video_file}' that needs a solution. Analyze the content carefully and provide a clear, well-crafted response. Make sure the solution is thorough and sophisticated, but keep the explanation brief and focused."""

        model = general_model

    my_video_file = genai.upload_file(path=video_file)
    while my_video_file.state.name == "PROCESSING":
        time.sleep(5)
        my_video_file = genai.get_file(my_video_file.name)
    
    video_response = model.generate_content([my_video_file, prompt])
    return video_response.text


audio_file = "output.wav"
video_file = "output.mp4"

