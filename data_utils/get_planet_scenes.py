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
    API_KEY = 'PLAKce77cdd919f147cc8f5754110aa562c6'

client = api.ClientV1(api_key=API_KEY)

gauth = GoogleAuth(settings_file='settings.yaml')
drive = GoogleDrive(gauth)

def search(geometry, start_date, end_date, cc):
    """Retrieve search
    ----
    Args:
        geometry: geojson for the sites
        start_date: "2020-04-01T00:00:00.000Z"
        end_date: same format as start_date
        cc: cloud cover in 0.05 (5%)
    """

    print('geometry: ', geometry)
    print('collections: PSScene')
    print('start_date, end_date: ', start_date, end_date)
    print('cc: ', cc)

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

    return results


def download_tif_files(q_result,
                       dir_path='/Users/guyyehezkel/Desktop/InformationSystems/third_year/finalProject/'
                                'Final_project/data_utils/searches/'):
    print(os.path.abspath(os.getcwd()))

    num_returned_obj = len(q_result.get())

    save_dir = dir_path + str(datetime.datetime.now())

    os.mkdir(save_dir)

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
        print(item)
        for k, v in item.items():
            print(k)
            print(v)
            print("==========================================================================")
        print("Item ID: ".format(item['id']))

        assets = client.get_assets(item).get()
        client.activate(assets['ortho_visual'])

        callback = api.write_to_file(directory=item_dir_name)

        # print(type(assets))
        for k, v in assets['ortho_visual'].items():
            print(k)
            print(v)
            print("==========================================================================")

        # print(assets['ortho_visual']['status'])

        # while assets['ortho_visual']['status'] != "active":
        #     print("activation status is: " + assets['ortho_visual']['status'] + ". waiting to be in 'active' status.")
        #     time.sleep(10)

        body = client.download(assets['ortho_visual'], callback=callback)
        body.wait

        while not glob.glob(item_dir_name + "/*.tif"):
            time.sleep(2)
            reload_directory(item_dir_name)
            print("waiting")

        # Iterate through all files in the directory
        for filename in os.listdir(item_dir_name):

            # Check if the file is an image file
            if filename.endswith('.tif'):
                full_path_tif = item_dir_name + "/" + filename
                split_image(image_path=full_path_tif, tile_size=256)


def reload_directory(directory):
    """
    Reload the contents of the given directory from disk.
    """
    # get a list of all files and directories in the directory
    files = os.listdir(directory)

    # loop through each file or directory and create the full path
    for filename in files:
        full_path = os.path.join(directory, filename)

        # if the file is a subdirectory, recursively reload its contents
        if os.path.isdir(full_path):
            reload_directory(full_path)


def split_image(image_path, tile_size):
    """
    Split a large image into smaller tiles.

    Parameters:
    image_path (str): The path to the TIF image.
    tile_size (int): The size of the tiles to split the image into.

    Returns:
    None
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

            # Save the tile
            tile.convert('RGB').save(f"{file_dir}/tiles/tile_{x}_{y}.jpg", 'JPEG', quality=100)




# =======================================================================================================#
#                                     Previous Helper functions                                         #
# =======================================================================================================#

def wait_until(predicate, timeout, period=0.25, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if predicate(*args, **kwargs): return True
        time.sleep(period)
    return False

def download_jpeg_files(
        dir_path='/Users/guyyehezkel/Desktop/InformationSystems/third_year/'
                 'finalProject/Final_project/data_utils/tif_files'):
    print(os.path.abspath(os.getcwd()))

    # Iterate through all files in the directory
    for filename in os.listdir(dir_path):

        # Check if the file is an image file
        if filename.endswith('.tif'):
            full_path_tif = dir_path + "/" + filename

            # Open the TIFF file
            with Image.open(full_path_tif) as tiff_image:
                # Resize the image to reduce its dimensions
                resized_image = tiff_image.resize((256, 256))

                dst_jpeg_name = '/Users/guyyehezkel/Desktop/InformationSystems/third_year/finalProject/Final_project/data_utils/jpeg_files/' + filename + '.jpg'

                # Convert the image to JPEG format
                resized_image.convert('RGB').save(dst_jpeg_name, 'JPEG', quality=100)

    print("end successfully!")
