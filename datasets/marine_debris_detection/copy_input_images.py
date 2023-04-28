import os
import shutil

INPUT_FOLDER_PATH = 'roboflow_marine_debris_input/'
DEST_FOLDER_PATH = 'marine_debris-semantic_segmentation/dataset/'


def copy_input_img_to_after_proccessed_folder(input_folder_path: str, dest_folder: str):
    """
    Copy images to the marine debris dataset folder
    Args:
        input_folder_path (str): path of input images
        dest_folder (str): path of images and masks after pre-processing.
    """
    for filename in os.listdir(dest_folder):
        filename = filename.split('.')[0] + '.jpg'
        current_path = os.path.join(input_folder_path, filename)
        new_path = os.path.join(dest_folder, filename)
        shutil.copy(current_path, new_path)


if __name__ == "__main__":
    copy_input_img_to_after_proccessed_folder(input_folder_path=INPUT_FOLDER_PATH, dest_folder=DEST_FOLDER_PATH)
