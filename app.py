from flask import Flask, request, jsonify, render_template
import os, torchaudio, torch
from seamless_communication.models.inference import Translator
import platform
from pydub import AudioSegment

app = Flask(__name__)
translator = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])

def translate():
    try:
        s2st_target_language_codes = {
            "English" : "eng",
            "Modern Standard Arabic" : "arb",
            "Bengali" : "ben",
            "Catalan" : "cat",
            "Czech" : "ces",
            "Mandarin Chinese" : "cmn",
            "Welsh" : "cym",
            "Danish" : "dan",
            "German" : "deu",
            "Estonian" : "est",
            "Finnish" : "fin",
            "French" : "fra",
            "Hindi" : "hin",
            "Indonesian" : "ind",
            "Italian" : "ita",
            "Japanese" : "jpn",
            "Korean" : "kor",
            "Maltese" : "mlt",
            "Dutch" : "nld",
            "Western Persian" : "pes",
            "Polish" : "pol",
            "Portuguese" : "por",
            "Romanian" : "ron",
            "Russian" : "rus",
            "Slovak" : "slk",
            "Spanish" : "spa",
            "Swedish" : "swe",
            "Swahili" : "swh",
            "Telugu" : "tel",
            "Tagalog" : "tgl",
            "Thai" : "tha",
            "Turkish" : "tur",
            "Ukrainian" : "ukr",
            "Urdu" : "urd",
            "Northern Uzbek" : "uzn",
            "Vietnamese" : "vie",
        }

        target_language = s2st_target_language_codes[str(request.form['targetLanguage'])]
    
        if 'recordedAudio' in request.files:
            recordedAudio = request.files['recordedAudio'] 
            selectedAudio = request.form['selectedAudio']
        elif 'selectedAudio' in request.files:
            selectedAudio = request.files['selectedAudio']
            recordedAudio = request.form['recordedAudio']
        else :
            selectedAudio = request.form['selectedAudio']
            recordedAudio = request.form['recordedAudio']

        return jsonify(validate_audio_file(recordedAudio, selectedAudio, target_language))

    except Exception as e:
        return jsonify({'error': str(e)}) 
    

def validate_audio_file(recordedAudio, selectedAudio, target_language):
    try:
        output_directory = 'static'
        os.makedirs(output_directory, exist_ok=True)

        global translator
        if len(str(translator)) == 0:
          translator = Translator("seamlessM4T_large", "vocoder_36langs", torch.device("cpu"), torch.float32)

        if(len(str(selectedAudio)) > 0) :
            if platform.system() == "Linux" or platform.system() == "Linux2":
                path = '/'
            for root, dir, files in os.walk(path):
                if selectedAudio.filename in files:
                    filePath = str(os.path.join(root, selectedAudio.filename))
        else:
            recordedAudio.save(os.path.join(output_directory, 'recorded_audio.wav'))
            filePath = str(os.path.join(output_directory, 'recorded_audio.wav'))
            audio = AudioSegment.from_file(filePath)
            audio = audio.set_frame_rate(16000)
            audio.export(filePath, format="wav")

        print("filePath " + filePath)
        text, wav, sr = translator.predict(filePath, 's2st', target_language)
    
        # Save the output waveform to a file
        torchaudio.save(os.path.join(output_directory, 'output.wav'),  wav[0].cpu(),  (sr))
        # Prepare the response
        response = {'text': str(text), 'audio_url': 'static/output.wav'}

        print(text)

        return response
        
    except Exception as e:
        print("Error:", e)
        return {'error': str(e)}

if __name__ == '__main__':
  app.run(port=8000)
