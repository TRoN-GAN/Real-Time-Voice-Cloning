# Initializing all the encoder libraries
from IPython.display import Audio
from IPython.utils import io
from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
import os
import multiprocessing 


def generate_audio(audioId, text_prompt, encoder, synthesizer, vocoder, reference_audio_path):

    print("[1] Fetching Reference Audio")
    # Fetching the reference audio
    in_fpath = Path(reference_audio_path)

    print("[2] Generating the Audio Features")
    preprocessed_wav = encoder.preprocess_wav(in_fpath)
    original_wav, sampling_rate = librosa.load(in_fpath)
    preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)
    embed = encoder.embed_utterance(preprocessed_wav)

    print("[3] Generating Audio")
    with io.capture_output() as captured:
        specs = synthesizer.synthesize_spectrograms([text_prompt], [embed])

    generated_wav = vocoder.infer_waveform(specs[0])
    generated_wav = np.pad(
        generated_wav, (0, synthesizer.sample_rate), mode="constant")

    print("[4] Saving the Audio")
    # Saving the Generated Audio file
    audio_file_path = os.path.join("static", "audio" + audioId + ".wav")
    sf.write(audio_file_path, generated_wav, synthesizer.sample_rate)

    return audio_file_path


def generate_audiobook_file(audioId, text_prompt, encoder, synthesizer, vocoder, reference_audio_path, WORD_SKIP_COUNT = 17):


    print("[1] Fetching Reference Audio")
    # Fetching the reference audio
    in_fpath = Path(reference_audio_path)

    print("[2] Generating the Audio Features")
    preprocessed_wav = encoder.preprocess_wav(in_fpath)
    original_wav, sampling_rate = librosa.load(in_fpath)
    preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)
    embed = encoder.embed_utterance(preprocessed_wav)

    print("[3] Generating the Speech")
    audiobookArray = np.array([])
    # Splitting the text prompt sentence wise
    words = text_prompt.split(" ")
    for wordIdx in range(0, len(words), WORD_SKIP_COUNT):

        sentence = " ".join(words[wordIdx : wordIdx+WORD_SKIP_COUNT])
        print(f"[Current Sentence] {sentence} \n")

        with io.capture_output() as captured:
            specs = synthesizer.synthesize_spectrograms([sentence], [embed])

        generated_wav = vocoder.infer_waveform(specs[0])
        audiobookArray = np.concatenate((audiobookArray, generated_wav), axis=0)
    
    # Padding
    # audiobookArray = np.pad(
    #     audiobookArray, (0, synthesizer.sample_rate), mode="constant")

    print("\n [5] Saving generated audiobook")
    # Saving the Generated Audio file
    audio_file_path = os.path.join("static", "audio" + audioId + ".wav")
    sf.write(audio_file_path, audiobookArray, synthesizer.sample_rate)

    return audio_file_path

