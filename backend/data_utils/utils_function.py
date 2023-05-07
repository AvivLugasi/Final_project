import json


def parse_date_time(date_time_str: str):
    """
    parse the date and time components of a date time string and return them as a list
    :param date_time_str: datetime string in the following format: 'YYYY-MM-DD HH:MM'
    :return: list of date time components of this format [year, month, day, hour, minute]
    """
    date_time_splited = date_time_str.split(" ")
    date_components_splited = date_time_splited[0].split("-")
    time_components_splited = date_time_splited[1].split(":")

    return [int(date_components_splited[0]), int(date_components_splited[1]), int(date_components_splited[2]),
            int(time_components_splited[0]), int(time_components_splited[1])]


def extract_geometry_timerange_from_json(path_to_json):
    """
    This function get as input path to json file was download from our web ui,
    then extract type cordinates and time range and return a variable which is input to the method "search" on data utils.
    :param path_to_json:
    :return: dictionary that using as input to search method in /data_utils/get_planet_scenes.py
    """
    with open(path_to_json) as f:
        json_data = json.load(f)

    search_data = json_data['features'][0]['geometry']
    start_date_time = parse_date_time(date_time_str=json_data['features'][0]['properties']['selectedDateRange']['start'])
    end_date_time = parse_date_time(date_time_str=json_data['features'][0]['properties']['selectedDateRange']['end'])
    start_date_time_formatted = create_time_string(year=start_date_time[0],
                                                  month=start_date_time[1],
                                                  day=start_date_time[2],
                                                  hour=start_date_time[3],
                                                  minute=start_date_time[4])
    end_date_time_formatted = create_time_string(year=end_date_time[0],
                                                  month=end_date_time[1],
                                                  day=end_date_time[2],
                                                  hour=end_date_time[3],
                                                  minute=end_date_time[4])
    search_dict = {
        "type": search_data['type'],
        "coordinates": search_data['coordinates'],
        "size": 256,
        "output_format": "jpeg"
    }
    return search_dict, start_date_time_formatted, end_date_time_formatted


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


def main(j_path: str = "D:/Downloads/data_1682785129202.geojson"):
    return extract_geometry_timerange_from_json(j_path)


if __name__ == "__main__":
    main()
