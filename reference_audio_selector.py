import os
import random
'''
Type : 
    "gender" : For gender only Generation
    "both" :   For age group and gender

'''
def get_reference_audio_path(type, sex = 0, ageGroup = "20-30"):

    # No path chosen state
    reference_audio_path = None

    if(type == "gender"):

        ref_male_audio_path = os.path.join("data", "ref_audios", "2002-139469-0019.flac")
        ref_female_audio_path = os.path.join("data", "ref_audios", "2007-149877-0001.flac")
        reference_audio_path = ref_male_audio_path if (int(sex)) else ref_female_audio_path

    elif type == "both":

        gender_word = "Male" if (int(sex)) else "Female"
        reference_audio_dir_path = os.path.join("data", "ref_audio", ageGroup, gender_word)
        
        ref_audio_name = random.sample(os.listdir(reference_audio_dir_path), 1)[0]
        
        reference_audio_path = os.path.join(reference_audio_dir_path, ref_audio_name)

    else:
        print("[ERROR] Incorrect type chosen for reference audio")

    print(f"[REFERENCE AUDIO] {reference_audio_path}")
    return reference_audio_path
