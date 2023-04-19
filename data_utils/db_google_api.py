from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.errors import HttpError
import datetime

gauth = GoogleAuth(settings_file='settings.yaml')
drive = GoogleDrive(gauth)
# upload_file_list = ['/Users/guyyehezkel/Desktop/InformationSystems/third_year/finalProject/Final_project/data_utils/searches/2023-04-08 18:59:26.010462/20161008_073252_0e3a/tiles/tile_0_2.jpg']
# for upload_file in upload_file_list:
#     gfile = drive.CreateFile()
#     # Read file and set it as the content of this instance.
#     gfile.SetContentFile(upload_file)
#     # Upload the file.
#     gfile.Upload()

def create_folder(dir_name: str):
    """ Create a folder and prints the folder ID
    Returns : Folder Id
    Load pre-authorized user credentials from the environment.
    """
    try:
        # create drive api client
        file_metadata = {
            'parents': [{'id': '1AwDcyFJJr85oFQMkGdBbm3QkS2Ye_1gB'}],
            'title': dir_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        # pylint: disable=maybe-no-member
        gfile = drive.CreateFile(file_metadata)
        gfile.Upload()
        print(F'Folder ID: "{gfile.get("id")}".')
        return gfile.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None

def upload_to_folder(folder_id, file_name, file):
    """Upload a file to the specified folder and prints file ID, folder ID
    Args: Id of the folder
    Returns: ID of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    d_f_id = {}
    d_f_id['id'] = folder_id
    try:
        file_metadata = {
            'title': file_name,
            'parents': [d_f_id],
            'mimetype': 'application/vnd.google-apps.file'
        }

        gfile = drive.CreateFile(file_metadata)
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(file)
        # Upload the file.
        gfile.Upload()

        print(F'File ID: "{gfile.get("id")}".')
        return gfile.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


if __name__ == '__main__':
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    folder_id = create_folder(dir_name=current_time)
    upload_to_folder(folder_id=folder_id,
                     file_name='image',
                     file='/Users/guyyehezkel/Desktop/InformationSystems/third_year/finalProject/Final_project/data_utils/searches/2023-04-08 18:59:26.010462/20161008_073252_0e3a/tiles/tile_0_2.jpg')