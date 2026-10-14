import glob
import os.path
import shutil
import string
import time
from pathlib import Path

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FOLDER = ACTIVITY_DIR / "data"
INPUT_FOLDER = ACTIVITY_DIR / "temp" / "input"
OUTPUT_FOLDER = ACTIVITY_DIR / "temp" / "output"
SUBMISSION_FOLDER = ACTIVITY_DIR / "submission"


def clear_folder(folder):
    if os.path.exists(folder):
        for file in glob.glob(f"{folder}/*"):
            os.remove(file)


def initialize_folder(folder):
    if os.path.exists(folder):
        clear_folder(folder)
    else:
        os.makedirs(folder)


def delete_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)


# Genera copias de los archivos en raw/
# -----------------------------------------------------------------------------


def generate_file_copies(n):

    for file in glob.glob(f"{DATA_FOLDER}/*"):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()

        for i in range(1, n + 1):
            raw_filename_with_extension = os.path.basename(file)
            raw_filename_without_extension = os.path.splitext(
                raw_filename_with_extension
            )[0]
            new_filename = f"{raw_filename_without_extension}_{i:05d}.txt"
            with open(f"{INPUT_FOLDER}/{new_filename}", "w", encoding="utf-8") as f2:
                f2.write(text)


# Mapper
# -----------------------------------------------------------------------------


def mapper(sequence):
    pairs_sequence = []
    for _, line in sequence:
        line = line.lower()
        line = line.translate(str.maketrans("", "", string.punctuation))
        line = line.replace("\n", "")
        words = line.split()
        pairs_sequence.extend([(word, 1) for word in words])
    return pairs_sequence


# Reducer
# -----------------------------------------------------------------------------


def reducer(pairs_sequence):
    result = []
    for key, value in pairs_sequence:
        if result and result[-1][0] == key:
            result[-1] = (key, result[-1][1] + value)
        else:
            result.append((key, value))
    return result


# Reducer
# -----------------------------------------------------------------------------


def hadoop(input_folder, output_folder, mapper_fn, reducer_fn):

    def read_records_from_input(input_folder):
        sequence = []
        files = glob.glob(f"{input_folder}/*")
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    sequence.append((file, line))
        return sequence

    def save_results_to_output(result):

        with open(
            os.path.join(output_folder, "part-00000"), "w", encoding="utf-8"
        ) as f:
            for key, value in result:
                f.write(f"{key}\t{value}\n")

    def create_success_file(output_folder):
        with open(os.path.join(output_folder, "_SUCCESS"), "w", encoding="utf-8") as f:
            f.write("")

    def create_output_directory(output_folder):
        if os.path.exists(output_folder):
            raise FileExistsError(f"The folder '{output_folder}' already exists.")
        else:
            os.makedirs(output_folder)

    sequence = read_records_from_input(input_folder)
    pairs_sequence = mapper_fn(sequence)
    pairs_sequence = sorted(pairs_sequence)
    result = reducer_fn(pairs_sequence)
    create_output_directory(output_folder)
    save_results_to_output(result)
    create_success_file(output_folder)


def copy_hdfs_output_to_submission(output_folder, submission_folder):
    initialize_folder(submission_folder)
    for file in glob.glob(f"{output_folder}/*"):
        shutil.copy2(file, submission_folder)


if __name__ == "__main__":

    initialize_folder(INPUT_FOLDER)
    delete_folder(OUTPUT_FOLDER)
    generate_file_copies(1000)
    start_time = time.time()

    hadoop(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        mapper_fn=mapper,
        reducer_fn=reducer,
    )
    copy_hdfs_output_to_submission(OUTPUT_FOLDER, SUBMISSION_FOLDER)

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")