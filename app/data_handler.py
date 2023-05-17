import os
from skimage import io
import json

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

                for tile_resource in os.listdir(tile_path):
                    if '.jpg' in tile_resource and "prediction" not in tile_resource:
                        image_path = os.path.join(tile_path, tile_resource)
                        image = io.imread(image_path)
                        # this is the json with the coordinates
                        json_name = tile_resource[:-4] + '.json'
                        json_path = os.path.join(tile_path, json_name)
                        with open(json_path, 'r') as file:
                            coordinates = json.load(file)
                        model_input.append({
                                        "image": image,
                                        "image_path": image_path,
                                        "coordinates": coordinates})
    return model_input


def writing_results(results_list, path_to_predictions):
    """
    write the positive predicted images to the folders of their
    correspond input image and delete the folders of the negative predicted images.
    args:
        results_list: list of lists of image, predictions, prediction indicator
        (1= the model predicted a debris in the image, 0 otherwise) and
        the path to the input image.
        path_tp_predictions: path to folder where the images and their results will be written to.
    """
    os.makedirs(path_to_predictions, exist_ok=True)
    for result in results_list:
        if result[2] == 1:
            image_name = os.path.basename(result[3])
            prediction_name = image_name[:-4] + 'prediction.jpg'
            prediction_path = os.path.join(path_to_predictions, prediction_name)
            image_path = os.path.join(path_to_predictions, image_name)
            json_name = image_name[:-4] + '.json'
            json_path = os.path.join(path_to_predictions, json_name)
            io.imsave(image_path, result[0])
            io.imsave(prediction_path, result[1])
            with open(json_path, "w") as jc:
                json.dump(result[4], jc)
