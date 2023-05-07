import os
from skimage import io


def data_load(path_to_search_result):
    """
    Read the search results images to a list of pairs(image, image path).
    args:
        path_to_search_result(str): path to the folder that contain Planet search results.
    returns:
        list of pairs(image, image path).
    """
    model_input = []

    # Iterate over each item in the parent folder
    for item in os.listdir(path_to_search_result):
        item_path = os.path.join(path_to_search_result, item).replace("\\", "/")

        # Check if the item is a directory/folder
        if os.path.isdir(item_path):

            for tile_folder in os.listdir(item_path + "/tiles/"):
                tile_path = item_path + "/tiles/" + tile_folder + "/"

                for tile in os.listdir(tile_path):
                    if '.jpg' in tile and "prediction" not in tile:
                        image_path = os.path.join(tile_path, tile)
                        image = io.imread(image_path)
                        model_input.append({"image": image, "image_path": image_path})
    return model_input


def writing_results(results_list):
    """
    write the positive predicted images to the folders of their
    correspond input image and delete the folders of the negative predicted images.
    args:
        results_list: list of lists of image, predictions, prediction indicator
        (1= the model predicted a debris in the image, 0 otherwise) and
        the path to the input image.
    """
    for result in results_list:
        if result[2] == 1:
            file_path = result[3][:-4] + 'prediction.jpg'
            io.imsave(file_path, result[1])
