from googleapiclient.errors import HttpError

from get_planet_scenes import search, download_tif_files, split_image
from utils_function import extract_geometry_timerange_from_json


def main(jsone_file):
    geometry = {
        "type": "Polygon",
        # "coordinates": [
        #   [
        #     [
        #       35.09913098949562,
        #       33.09089339123881
        #     ],
        #     [
        #       34.94256438721459,
        #       33.09089339123881
        #     ],
        #     [
        #       34.94256438721459,
        #       32.808969466099484
        #     ],
        #     [
        #       35.09913098949562,
        #       32.808969466099484
        #     ],
        #     [
        #       35.09913098949562,
        #       33.09089339123881
        #     ]
        #   ]
        # ],
        # "coordinates": [
        #     [
        #         [
        #             -87.01171875,
        #             16.04581345375217
        #         ],
        #         [
        #             -87.01171875,
        #             16.040534227979766
        #         ],
        #         [
        #             -87.0062255859375,
        #             16.040534227979766
        #         ],
        #         [
        #             -87.0062255859375,
        #             16.04581345375217
        #         ],
        #         [
        #             -87.01171875,
        #             16.04581345375217
        #         ]
        #     ]
        # ],
        # north Israel
        # "coordinates": [
        #   [
        #     [
        #       34.94295696964002,
        #       33.105655120865165
        #     ],
        #     [
        #       34.94295696964002,
        #       32.80930655908928
        #     ],
        #     [
        #       35.101692142766524,
        #       32.80930655908928
        #     ],
        #     [
        #       35.101692142766524,
        #       33.105655120865165
        #     ],
        #     [
        #       34.94295696964002,
        #       33.105655120865165
        #     ]
        #   ]
        # ],
        #Haifa to TLV
        "coordinates": [
            [
                [
                    -87.1380615234375,
                    16.06692895745011
                ],
                [
                    -87.1380615234375,
                    16.06165029151658
                ],
                [
                    -87.132568359375,
                    16.06165029151658
                ],
                [
                    -87.132568359375,
                    16.06692895745011
                ],
                [
                    -87.1380615234375,
                    16.06692895745011
                ]
            ]
        ],
        "size": 256,
        "output_format": "jpeg"
    }

    # build a filter for the AOI
    max_cloud_percentage = 0.5
    # gte = "2019-08-31T00:00:00.000Z"
    # lte = "2019-09-01T00:00:00.000Z"
    gte = "2016-10-08T00:00:00Z"
    lte = "2016-10-09T00:00:00Z"

    geometry_json, start_date_time_formatted, end_date_time_formatted = extract_geometry_timerange_from_json("D:/Downloads/data_1683388714600.geojson")
    q_res = search(geometry=geometry_json, start_date=start_date_time_formatted
                   , end_date=end_date_time_formatted, cc=max_cloud_percentage)
    search_folder = download_tif_files(q_res)






    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive

    # gauth = GoogleAuth(settings_file='settings.yaml')
    # drive = GoogleDrive(gauth)
    # upload_file_list = ['/Users/guyyehezkel/Desktop/InformationSystems/third_year/finalProject/Final_project/data_utils/searches/2023-04-08 18:59:26.010462/20161008_073252_0e3a/tiles/tile_0_2.jpg']
    # for upload_file in upload_file_list:
    #     gfile = drive.CreateFile()
    #     # Read file and set it as the content of this instance.
    #     gfile.SetContentFile(upload_file)
    #     # Upload the file.
    #     gfile.Upload()




if __name__ == "__main__":
    main()
