import pandas as pd
import copy
import os
import glob

search_dict_structure = {
    "20-25": {
        '0': [],
        '1': []
    },
    "25-30": {
        '0': [],
        '1': []
    },
    "30-35": {
        '0': [],
        '1': []
    },
    "35-40": {
        '0': [],
        '1': []
    },
    "40-45": {
        '0': [],
        '1': []
    },
    "45-50": {
        '0': [],
        '1': []
    },
    "50-55": {
        '0': [],
        '1': []
    },
    "55-60": {
        '0': [],
        '1': []
    },
    "60-75": {
        '0': [],
        '1': []
    }
}


def get_age_group(age):
    age = int(age)

    if(age >= 20 and age < 25):
        return "20-25"
    elif (age >= 25 and age < 30):
        return "25-30"
    elif (age >= 30 and age < 35):
        return "30-35"
    elif (age >= 35 and age < 40):
        return "35-40"
    elif (age >= 40 and age < 45):
        return "40-45"
    elif (age >= 45 and age < 50):
        return "45-50"
    elif (age >= 50 and age < 55):
        return "50-55"
    elif (age >= 55 and age < 60):
        return "55-60"
    else:
        return "60-75"

# As of now by default only happy audios are taken


def form_CREMAD_file_path(audio_dir_path, personID, prompt="TAI", emotion="HAP", emotion_level="MD"):

    filenames = glob.glob(
        f"{audio_dir_path}/{personID}_{prompt}_{emotion}_*.wav")

    return filenames[0]


def generate_CREMAD_search_dict(meta_data_file_path, audio_dir_path):

    # Loading the Metadata file
    demographics = pd.read_csv(meta_data_file_path)

    # Iterating over demographics and creating search dict
    search_dict = copy.deepcopy(search_dict_structure)

    for index, row in demographics.iterrows():

        # Finding the age group and gender
        age_group = get_age_group(row['Age'])
        gender = "0" if row["Sex"] == "Female" else "1"

        # Appending the file path to the list
        search_dict[age_group][gender].append(
            form_CREMAD_file_path(audio_dir_path, row["ActorID"]))

    return search_dict


if __name__ == "__main__":
    meta_data_file_path = os.path.join(
        "data", "CREMAD", "VideoDemographics.csv")
    audio_dir_path = os.path.join("data", "CREMAD", "AudioWAV")
    search_dict = generate_CREMAD_search_dict(
        meta_data_file_path, audio_dir_path)
    print(search_dict)
