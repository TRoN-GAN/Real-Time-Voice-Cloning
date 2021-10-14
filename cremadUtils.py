import pandas as pd
import copy
import os
import shutil
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


age_directories = ["20-25", "25-30", "30-35", "35-40",
                   "40-45", "45-50", "50-55", "55-60", "60-75"]

gender_directories = ["Male", "Female"]


def organize_cremad(meta_data_file_path, source_dir,  target_dir, group_by="age group"):

    # Get a list of all the files in the source directory
    audio_files = os.listdir(source_dir)
    num_audio_files = len(audio_files)

    # Making the target directory
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
    os.mkdir(target_dir)

    # Loading the Metadata file and making a search dict
    demographics = pd.read_csv(meta_data_file_path)

    person_info = {}
    for index, row in demographics.iterrows():
        print(row)
        person_info[str(row["ActorID"])] = {
            "Age": row["Age"], "Sex": row["Sex"]}

    # Creating the group directories
    print(f"[INFO] Grouping by {group_by}")
    if group_by == "age group":

        # Making the group directories
        for group in age_directories:
            os.mkdir(os.path.join(target_dir, group))

        # Loop to copy files from source_dir to target_dir
        for audio_file in audio_files:

            # Obtaining person ID
            person_ID = str(audio_file.split("_")[0])

            # Obtaining the Age Group
            age_group = get_age_group(person_info[person_ID]["Age"])

            # Getting Source and destination paths
            source_audio_path = os.path.join(source_dir, audio_file)
            destination_audio_path = os.path.join(
                target_dir, age_group, audio_file)

            # Copying the file
            shutil.copyfile(source_audio_path, destination_audio_path)
            print(f"Person {person_ID}, Age Group : {age_group}")
            print(f"Copying the file to {destination_audio_path}")
            print()

    elif group_by == "gender":

        # Making the group directories
        for group in gender_directories:
            os.mkdir(os.path.join(target_dir, group))

        # Loop to copy files from source_dir to target_dir
        for audio_file in audio_files:

            # Obtaining person ID
            person_ID = str(audio_file.split("_")[0])

            # Obtaining the Age Group
            gender = row["Sex"]

            # Getting Source and destination paths
            source_audio_path = os.path.join(source_dir, audio_file)
            destination_audio_path = os.path.join(
                target_dir, gender, audio_file)

            # Copying the file
            shutil.copyfile(source_audio_path, destination_audio_path)
            print(f"Person {person_ID}, Gender : {gender}")
            print(f"Copying the file to {destination_audio_path}")
            print()

    elif group_by == "both":

        # Making the group directories and nested gender directories
        for cur_age_group in age_directories:
            os.mkdir(os.path.join(target_dir, cur_age_group))
            for gender_group in gender_directories:
                os.mkdir(os.path.join(target_dir, cur_age_group, gender_group))

        # Loop to copy files from source_dir to target_dir
        for audio_file in audio_files:

            # Obtaining person ID
            person_ID = str(audio_file.split("_")[0])

            # Obtaining the Age Group
            age_group = get_age_group(person_info[person_ID]["Age"])
            gender = row["Sex"]

            # Getting Source and destination paths
            source_audio_path = os.path.join(source_dir, audio_file)
            destination_audio_path = os.path.join(
                target_dir, age_group, gender, audio_file)

            # Copying the file
            shutil.copyfile(source_audio_path, destination_audio_path)
            print(
                f"Person {person_ID}, Age Group {age_group}, Gender : {gender}")
            print(f"Copying the file to {destination_audio_path}")
            print()

    else:
        print(
            f"[ERROR] Invalid value for the argument 'group_by' : {group_by}")



if __name__ == "__main__":
    meta_data_file_path = os.path.join(
        "data", "CREMAD", "VideoDemographics.csv")
    # audio_dir_path = os.path.join("data", "CREMAD", "AudioWAV")
    # search_dict = generate_CREMAD_search_dict(
    #     meta_data_file_path, audio_dir_path)
    # print(search_dict)

    source_dir = os.path.join("data", "CREMAD", "AudioWAV")
    target_dir = os.path.join("data", "grouped_cremad")

    '''
    group_by = "age group"
    This must be passed to group audios by age group

    group_by = "gender
    This must be passed to group audios by gender

    group_by = "both"
    This must be passed to group audios by age group and gender
    '''
    organize_cremad(meta_data_file_path, source_dir,
                    target_dir, group_by="both")
