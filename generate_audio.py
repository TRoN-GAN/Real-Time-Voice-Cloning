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
import concurrent.futures
from enhance import trim_long_silences, normalize_volume

from encoder import inference as encoder
from vocoder import inference as vocoder
from synthesizer.inference import Synthesizer


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
    
    # enhancing the generated wav
    norm_wav = normalize_volume(generated_wav, -30)
    trim_wav = trim_long_silences(norm_wav)
   
    sf.write(audio_file_path, trim_wav, synthesizer.sample_rate)

    return audio_file_path

# Function to generate audio data per sentence
def generate_sentence_audio(iteration, sentence, embed):
    print(f"Generating for sentence {iteration+1}")
    saved_model = "pretrained"
    encoder_weights = Path(f"encoder/saved_models/{saved_model}.pt")
    vocoder_weights = Path(f"vocoder/saved_models/pretrained/pretrained.pt")
    syn_dir = Path(f"synthesizer/saved_models/pretrained/pretrained.pt")

    encoder.load_model(encoder_weights)
    synthesizer = Synthesizer(syn_dir)
    vocoder.load_model(vocoder_weights)

    with io.capture_output() as captured:
            specs = synthesizer.synthesize_spectrograms([sentence], [embed])

    generated_wav = vocoder.infer_waveform(specs[0])

    # enhancing the generated wav
    norm_wav = normalize_volume(generated_wav, -30)
    trim_wav = trim_long_silences(norm_wav)

    return (iteration, trim_wav)
    
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

    # Forming the sentences array on which the processing will happen
    words = text_prompt.split(" ")
    sentences = []
    for wordIdx in range(0, len(words), WORD_SKIP_COUNT):
        sentences.append(" ".join(words[wordIdx : wordIdx+WORD_SKIP_COUNT]))

    # Finding the number of sentences
    NUM_SENTENCES = len(sentences)

    # Results array that will hold audio data for each sentence
    auido_data_for_sentences = ["Gullu" for i in range(NUM_SENTENCES)]


    # Multiprocessing code to generate audio data in parallel for sentences
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(generate_sentence_audio, iteration, sentences[iteration], embed) for iteration in range(NUM_SENTENCES)]

        for f in concurrent.futures.as_completed(results):
            auido_data_for_sentences[f.result()[0]] = f.result()[1]

    # stitching together the audio data of all sentences into one 
    # Empty Audiobook data array which will hold the results
    audiobookArray = np.array([])
    for sentence_audio in auido_data_for_sentences:
        audiobookArray = np.concatenate((audiobookArray, sentence_audio), axis=0)

    # Padding
    audiobookArray = np.pad(
        audiobookArray, (0, synthesizer.sample_rate), mode="constant")

    print("\n [5] Saving generated audiobook")
    # Saving the Generated Audio file
    audio_file_path = os.path.join("static", "audio" + audioId + ".wav")

    sf.write(audio_file_path, audiobookArray, synthesizer.sample_rate)

    return audio_file_path

