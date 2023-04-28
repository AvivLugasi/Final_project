import json


def extract_geometry_from_json(path_to_json):
    """
    This function get as input path to json file was download from our web ui,
    then extract type and cordinates and return an variable which is input to the method "search" on data utils.
    :param path_to_json:
    :return: dictionary that using as input to search method in /data_utils/get_planet_scenes.py
    """
    with open(path_to_json) as f:
        json_data = json.load(f)

    geometry_data = json_data['features'][0]['geometry']

    geometry = {
        "type": geometry_data['type'],
        "coordinates": geometry_data['coordinates'],
        "size": 256,
        "output_format": "jpeg"
    }
    return geometry


def create_time_string(year: int, month: int, day: int, hour: int = 0, minute: int = 0):
    """
    This function get time parameters and return string represent the requested time
    :param year: e.g. "2010" (4 digits)
    :param month: e.g. 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 , 11, 12
    :param day: no zero padding needed for example use "1" not "01"
    :param hour: no zero padding needed
    :param minute: no zero padding needed
    :return: string. looks like "2016-10-08T10:10:00Z"
    """
    datetime_str = f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00Z"
    return datetime_str


def main():
    # j_path = "aoi_jason_files/data_1682595028543.geojson"
    # geometry = extract_geometry_from_json(j_path)
    # print(geometry)
    gte = create_time_string(year=2016, month=10, day=8, hour=10, minute=10)
    print(gte)
    # "2016-10-08T00:00:00Z"


if __name__ == "__main__":
    main()
