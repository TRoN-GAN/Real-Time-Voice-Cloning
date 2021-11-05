import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from pathlib import Path
from encoder import inference as encoder
from vocoder import inference as vocoder
from synthesizer.inference import Synthesizer

from reference_audio_selector import get_reference_audio_path
from generate_audio import generate_audio, generate_audiobook_file
from cremadUtils import generate_CREMAD_search_dict

app = Flask(__name__, static_folder='static')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['FILE_UPLOADS'] = os.path.join("static", "uploaded")

# GLOBAL VARIABLES
REF_AUDIO_TYPE = 'gender'

# Loading the Models and keeping them ready for use
# Loading the pretrained model
print("[*] Loading pretrained Models")

saved_model = "pretrained"
encoder_weights = Path(f"encoder/saved_models/{saved_model}.pt")
vocoder_weights = Path(f"vocoder/saved_models/pretrained/pretrained.pt")
syn_dir = Path(f"synthesizer/saved_models/pretrained/pretrained.pt")

encoder.load_model(encoder_weights)
synthesizer = Synthesizer(syn_dir)
vocoder.load_model(vocoder_weights)

print("[*] Making the Static Folder if not present already")
if not os.path.isdir("static"):
    os.mkdir("static")

if not os.path.isdir("static/uploaded"):
    os.mkdir("static/uploaded")

print("[*] Loading reference audios from CREMAD")
meta_data_file_path = os.path.join(
    "..", "DATASETS", "CREMAD", "VideoDemographics.csv")
audio_dir_path = os.path.join("..", "DATASETS", "CREMAD", "AudioWAV")

# Getting the search dict ready
# print("[*] Generating Search Dictionary for CREMAD")
# CREMAD_search_dict = generate_CREMAD_search_dict(
#     meta_data_file_path, audio_dir_path)methods


@app.route("/api/generate-audio", methods=["POST"])
@cross_origin()
def create_audio():

    # Retrieving the data from json
    request_content = request.get_json()

    audioId = request_content['audioId']
    text_prompt = request_content['prompt']
    sex = request_content['sex']
    ageGroup = request_content['age']

    print("--------------------------------------------------------------------->")
    print("Audio ID : ", audioId)
    print("Prompt : ", text_prompt)
    print("Sex : ", sex)
    print("Age Group : ", ageGroup)

    # Generation of Audio
    try:

        # # CREMAD BASED ONLY
        # Generate Audio Code goes here
        # reference_audio_path = CREMAD_search_dict[ageGroup][str(sex)][0]

        # Tracking time for generation
        start_time = time.time()
        # Getting Reference Audio Path
        reference_audio_path = get_reference_audio_path(
            REF_AUDIO_TYPE, sex, ageGroup)
        generated_audio_path = generate_audio(
            audioId, text_prompt, encoder, synthesizer, vocoder, reference_audio_path)

        # Tracking time for generation
        end_time = time.time()
        total_time = end_time - start_time

        # Returning the generated file
        return_val = {
            'status': 200,
            'statusText': "ok",
            'prompt': text_prompt,
            'url': generated_audio_path,
            'generationTime': total_time
        }

    except Exception as e:

        print("Internal Server Error")
        print("[ERROR] ", e)
        return_val = {
            'status': 500,
            'statusText': "Internal Server Error",
        }

    return jsonify(return_val)


@app.route("/api/generate-audiobook", methods=["POST"])
@cross_origin()
def generate_audiobook():

    # Retrieving the data from json
    request_content = request.get_json()

    audioId = request_content['audioId']
    text_prompt = request_content['prompt']
    sex = request_content['sex']
    ageGroup = request_content['age']

    print("--------------------------------------------------------------------->")
    print("Audio ID : ", audioId)
    print("Prompt : ", text_prompt)
    print("Sex : ", sex)
    print("Age Group : ", ageGroup)

    try:

        # Tracking time for generation
        start_time = time.time()

        reference_audio_path = get_reference_audio_path(
            REF_AUDIO_TYPE, sex, ageGroup)

        generated_audio_path = generate_audiobook_file(
            audioId, text_prompt, encoder, synthesizer, vocoder, reference_audio_path)

        # Tracking time for generation
        end_time = time.time()
        total_time = end_time - start_time

        # Returning the generated file
        return_val = {
            'status': 200,
            'statusText': "ok",
            'prompt': text_prompt,
            'url': generated_audio_path,
            'generationTime': total_time
        }

    except Exception as e:

        print("Internal Server Error")
        print("[ERROR] ", e)
        return_val = {
            'status': 500,
            'statusText': "Internal Server Error",
        }

    return jsonify(return_val)


@app.route("/api/generate-voice-clone", methods=["POST"])
@cross_origin()
def generate_voice_clone():

    # Retrieving the data from json
    request_content = request.get_json()

    audioId = request_content['audioId']
    text_prompt = request_content['prompt']
    reference_audio_path = os.path.join(
        "static", "uploaded", str(request_content['filename']))

    print("--------------------------------------------------------------------->")
    print(f"Request Content : {request_content}")
    print(f"Reference Audio : {reference_audio_path}")
    print("Audio ID : ", audioId)
    print("Prompt : ", text_prompt)

    try:

        # Tracking time for generation
        start_time = time.time()

        generated_audio_path = generate_audiobook_file(
            audioId, text_prompt, encoder, synthesizer, vocoder, reference_audio_path)

        # Tracking time for generation
        end_time = time.time()
        total_time = end_time - start_time

        # Returning the generated file
        return_val = {
            'status': 200,
            'statusText': "ok",
            'prompt': text_prompt,
            'url': generated_audio_path,
            'generationTime': total_time
        }

    except Exception as e:

        print("Internal Server Error")
        print("[ERROR] ", e)
        return_val = {
            'status': 500,
            'statusText': "Internal Server Error",
        }

    return jsonify(return_val)


@app.route("/api/upload/<path:filename>", methods=["POST"])
@cross_origin()
def upload_file(filename):
    # checking if the file is present or not
    if request.files:
        file = request.files[list(request.files)[0]]
        file.save(os.path.join(app.config['FILE_UPLOADS'], str(filename)))
        print(f"Uploaded {filename} successfully!")
        return jsonify({"status": 201, "msg": "File successfully saved !", "filename": filename})
    else:
        return jsonify({"status": 400, "msg": "No file received !"})


@app.route("/static/<path:filename>", methods=["GET"])
@cross_origin()
def fetch_audio(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True)
