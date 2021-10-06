import os
import time

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_folder='static')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/api/audio/generate", methods=["POST"])
@cross_origin()
def create_audio():

    # Retrieving the data from json
    request_content = request.get_json()

    text_prompt = request_content['prompt']
    sex = request_content['sex']
    # age = int(request_content['age'])
    # ethnicity = request_content['ethnicity']
    # race = request_content['race']
    # language = request_content['language']
    # emotion = request_content['emotion']
    # emotion_level = request_content['emotion_level']


    print("--------------------------------------------------------------------->")
    print("Prompt : ", text_prompt)
    print("Sex : ", sex)
    # print("Age : ", age)
    # print("Ethnicity : ", ethnicity)
    # print("race : ", race)
    # print("language : ", language)
    # print("emotion : ", emotion)
    # print("emotion_level : ",emotion_level)
    print("--------------------------------------------------------------------->")


    # Generation of Audio
    try:
        timestamp = str(time.time())

        
        myobj = gTTS(text=text_prompt, lang=language, slow=False)

        if os.path.isdir("static"):
            myobj.save(os.path.join("static", "audio" + str(timestamp) + ".wav"))
        else:
            os.mkdir("static") 
            myobj.save(os.path.join("static", "audio" + str(timestamp) + ".wav"))

        del myobj

        # Returning the generated file
        return_val = {
            'status': 200,
            'statusText': "ok",
            'prompt': text_prompt,
            'url': "/static/audio" + timestamp + ".wav"
        }

    except:

        print("Internal Server Error")
        return_val = {
            'status': 500,
            'statusText': "Internal Server Error",
        }

    return jsonify(return_val)


app.run(debug=True)


@app.route("/static/<path:filename>", methods=["GET"])
@cross_origin()
def fetch_audio(filename):

    return send_from_directory("static", filename)
