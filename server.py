import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from pathlib import Path
from encoder import inference as encoder
from vocoder import inference as vocoder
from synthesizer.inference import Synthesizer


from generate_audio import generate_audio
from cremadUtils import generate_CREMAD_search_dict

app = Flask(__name__, static_folder='static')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# Loading the Models and keeping them ready for use
# Loading the pretrained model
print("[*] Loading pretrained Models")
encoder_weights = Path("encoder/saved_models/pretrained.pt")
vocoder_weights = Path("vocoder/saved_models/pretrained/pretrained.pt")
syn_dir = Path("synthesizer/saved_models/pretrained/pretrained.pt")
encoder.load_model(encoder_weights)
synthesizer = Synthesizer(syn_dir)
vocoder.load_model(vocoder_weights)

print("[*] Making the Static Folder if not present already")
if not os.path.isdir("static"):
    os.mkdir("static")

print("[*] Loading reference audios from CREMAD")
meta_data_file_path = os.path.join("data", "CREMAD", "VideoDemographics.csv")
audio_dir_path = os.path.join("data", "CREMAD", "AudioWAV")

# Getting the search dict ready
print("[*] Generating Search Dictionary for CREMAD")
CREMAD_search_dict = generate_CREMAD_search_dict(
    meta_data_file_path, audio_dir_path)


@app.route("/api/generate-audio", methods=["POST"])
@cross_origin()
def create_audio():

    # Retrieving the data from json
    request_content = request.get_json()

    audioId = request_content['audioId']
    text_prompt = request_content['prompt']
    sex = request_content['sex']
    ageGroup = request_content['age']
    # ethnicity = request_content['ethnicity']
    # race = request_content['race']
    # language = request_content['language']
    # emotion = request_content['emotion']
    # emotion_level = request_content['emotion_level']

    print("--------------------------------------------------------------------->")
    print("Audio ID : ", audioId)
    print("Prompt : ", text_prompt)
    print("Sex : ", sex)
    print("Age Group : ", ageGroup)
    # print("Ethnicity : ", ethnicity)
    # print("race : ", race)
    # print("language : ", language)
    # print("emotion : ", emotion)
    # print("emotion_level : ",emotion_level)
    print("--------------------------------------------------------------------->")

    # Generation of Audio
    try:

        # Generate Audio Code goes here
        reference_audio_path = CREMAD_search_dict[ageGroup][str(sex)][0]
        print(f"[REFERENCE AUDIO] {reference_audio_path}")

        # ref_male_audio_path = os.path.join("data", "ref_audios", "2002-139469-0019.flac")
        # ref_female_audio_path = os.path.join("data", "ref_audios", "2007-149877-0001.flac")
        # reference_audio_path = ref_male_audio_path if (int(sex)) else ref_female_audio_path

        print("[*] Taking Ref Audio ", reference_audio_path)
        generated_audio_path = generate_audio(
            audioId, text_prompt, encoder, synthesizer, vocoder, reference_audio_path)

        # Returning the generated file
        return_val = {
            'status': 200,
            'statusText': "ok",
            'prompt': text_prompt,
            'url': generated_audio_path
        }

    except Exception as e:

        print("Internal Server Error")
        print("[ERROR] ", e)
        return_val = {
            'status': 500,
            'statusText': "Internal Server Error",
        }

    return jsonify(return_val)


@app.route("/static/<path:filename>", methods=["GET"])
@cross_origin()
def fetch_audio(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True)
