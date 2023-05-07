import time
from PIL import Image
import os
import json
import datetime
from planet import api
import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# if your Planet API Key is not set as an environment variable, you can paste it below
if os.environ.get('PL_API_KEY', ''):
    API_KEY = os.environ.get('PL_API_KEY', '')
else:
    # API_KEY = 'PLAKce77cdd919f147cc8f5754110aa562c6'
    API_KEY = 'PLAKa292687c4916440aa7f7be64d0b0269a'

client = api.ClientV1(api_key=API_KEY)

gauth = GoogleAuth(settings_file='settings.yaml')
drive = GoogleDrive(gauth)


def search(geometry, start_date, end_date, cc=0.5):
    """Retrieve search
    ----
    Args:
        geometry: geojson for the sites
        start_date: "2020-04-01T00:00:00.000Z"
        end_date: same format as start_date
        cc: cloud cover in 0.05 (5%)
    """

    # build a filter for the AOI
    query = api.filters.and_filter(
        api.filters.geom_filter(geometry),
        api.filters.date_range("acquired", gte=start_date, lte=end_date),
        api.filters.range_filter('cloud_cover', gt=0),
        api.filters.range_filter('cloud_cover', lt=float(cc))
    )

    # we are requesting PlanetScope 3 Band imagery
    item_types = ['PSScene']
    request = api.filters.build_search_request(query, item_types)

    # this will cause an exception if there are any API related errors
    results = client.quick_search(request)
    if not results:
        print("no results where been found for the requested time and/or coordinates")
    return results


def download_tif_files(q_result,
                       dir_path='/searches/'):
    """
    This function get all assets from Planet API based on given input.
    For each tiff file returned from the search, the function creates a folder with the property's id name,
    and stores the json file, the tiff file and a folder containing tiles of the tiff.
    :param q_result: query result from Plant API based on user input.
    :param dir_path:path to the directory you want the search will be saved in.
    """
    print("creating new dir in /data_utils/searchers/ named current time")

    num_returned_obj = len(q_result.get())

    save_dir = os.path.abspath(os.getcwd()).replace("\\", "/") \
               + dir_path + str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")

    os.makedirs(save_dir)

    print("call planet api to get query result that given as input")
    res = q_result.items_iter(num_returned_obj)

    # q_result_items is items_iter who returns an iterator over API response pages
    for item in res:

        item_dir_name = save_dir + "/" + item['id']

        # create the directory if it doesn't already exist
        if not os.path.exists(item_dir_name):
            os.mkdir(item_dir_name)

        # specify the path of the JSON file
        json_file_name = item['id'] + ".json"
        json_file_path = os.path.join(item_dir_name, json_file_name)

        # write the dictionary to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(item, json_file)

        # each item is a GeoJSON feature
        print("Get Item ID: ".format(item['id']))

        assets = client.get_assets(item).get()
        client.activate(assets['ortho_visual'])

        # wait until activation completes
        while True:
            assets = client.get_assets(item).get()
            # if assets["ortho_visual"].has_key("location"):
            if "location" in assets["ortho_visual"]:
                break
            print("waiting 10 sec before checking activation status again")
            time.sleep(10)

        print(item['geometry']['coordinates'])
        coordinates = item['geometry']['coordinates']

        callback = api.write_to_file(directory=item_dir_name)

        body = client.download(assets['ortho_visual'], callback=callback)
        body.wait()

        while not glob.glob(item_dir_name + "/*.tif"):
            time.sleep(2)
            reload_directory(item_dir_name)
            print("waiting 2 sec for the tiff file to be created")

        # Iterate through all files in the directory
        for filename in os.listdir(item_dir_name):

            # Check if the file is an image file
            if filename.endswith('.tif'):
                full_path_tif = item_dir_name + "/" + filename
                split_image(image_path=full_path_tif, tile_size=256, coordinates=coordinates)


def reload_directory(directory):
    """
    Reload the contents of the given directory from disk.
    :param directory: path to directory
    """
    # get a list of all files and directories in the directory
    files = os.listdir(directory)

    # loop through each file or directory and create the full path
    for filename in files:
        full_path = os.path.join(directory, filename)

        # if the file is a subdirectory, recursively reload its contents
        if os.path.isdir(full_path):
            reload_directory(full_path)


def split_image(image_path, tile_size, coordinates):
    """
    Split a large tiff image into smaller jpeg tiles.
    For each tile a folder is created with the name of the tile's relative position within the large image.
    ֿIn this folder two files are created: a 256*256 jpeg file of the tile and
    a json file containing the real world coordinates of the tile
    Parameters:
    :param image_path: (str): The path to the TIF image.
    :param tile_size: (int): The size of the tiles to split the image into.
    :param coordinates: list contains the coordinates of the large tiff image
    """
    # Open the image
    image = Image.open(image_path)

    # Get the size of the image
    width, height = image.size

    # Calculate the number of tiles in the x and y directions
    num_tiles_x = int(width / tile_size)
    num_tiles_y = int(height / tile_size)

    # Get the directory of the file path
    file_dir = os.path.dirname(image_path)

    # Create a new directory to save the tiles
    os.makedirs(file_dir + "/tiles", exist_ok=True)

    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            # Calculate the position of the tile
            x_pos = x * tile_size
            y_pos = y * tile_size

            # Crop the tile from the image
            tile = image.crop((x_pos, y_pos, x_pos + tile_size, y_pos + tile_size))

            # Create a new directory to save the tiles
            # os.makedirs(file_dir + "/tiles", exist_ok=True)
            os.makedirs(f"{file_dir}/tiles/tile_{x}_{y}", exist_ok=True)

            # Save the tile
            tile.convert('RGB').save(f"{file_dir}/tiles/tile_{x}_{y}/tile_{x}_{y}.jpg", 'JPEG', quality=100)

            # Calculate the coordinates of the tile in the world
            tile_left = coordinates[0][0][0] + (x_pos / width) * (coordinates[0][1][0] - coordinates[0][0][0])
            tile_right = coordinates[0][0][0] + ((x_pos + tile_size) / width) * (
                    coordinates[0][1][0] - coordinates[0][0][0])
            tile_top = coordinates[0][0][1] + (y_pos / height) * (coordinates[0][2][1] - coordinates[0][0][1])
            tile_bottom = coordinates[0][0][1] + ((y_pos + tile_size) / height) * (
                    coordinates[0][2][1] - coordinates[0][0][1])
            tile_coordinates = [[
                [tile_left, tile_top],
                [tile_right, tile_top],
                [tile_right, tile_bottom],
                [tile_left, tile_bottom],
                [tile_left, tile_top]
            ]]
            # Save the coordinates of the tile in a JSON file
            with open(f"{file_dir}/tiles/tile_{x}_{y}/tile_{x}_{y}.json", 'w') as f:
                json.dump(tile_coordinates, f)
