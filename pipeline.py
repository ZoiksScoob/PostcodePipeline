import sys
import csv
import pandas as pd
import datetime as dt
from geopy.distance import geodesic


def import_address_list(file_path):
    df = pd.read_csv(file_path)

    # Convert Latitude and Longitude to numeric types
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    # Convert Registration Date to timestamps
    df["Registration Date"] = pd.to_datetime(df["Registration Date"], errors="coerce")

    # Convert urn to numeric
    df["urn"] = pd.to_numeric(df["urn"], errors="coerce")

    # Create postcode column
    def get_postcode(location):
        if ',' in location:
            postcode = location.split(',')[-1].strip()
            return postcode
        return location

    df['Postcode'] = df['Location'].apply(get_postcode)

    return df


def import_postcode_reference(file_path):
    df = pd.read_csv(file_path)

    def custom_str_to_datetime(dt_str, dt_str_format='%Y%m'):
        try:
            if pd.isna(dt_str):
                return pd.NaT
            elif isinstance(dt_str, pd.Timestamp):
                return dt_str
            else:
                dt_str = str(dt_str)
                return dt.datetime.strptime(dt_str, dt_str_format)
        except ValueError:
            return pd.NaT

    # Convert postcode datetime columns to timestamps, setting to NaT what isn't a date
    df["postcode_introduced"] = df["postcode_introduced"].apply(custom_str_to_datetime)
    df["postcode_terminated"] = df["postcode_terminated"].apply(custom_str_to_datetime)

    return df


def create_columns(address_list, postcode_reference, coord_tol=1):
    merged = address_list.merge(postcode_reference, how='left', left_on='Postcode', right_on='postcode')

    # Perform the date range validation
    def check_date_within_range(record):
        date = record['Registration Date']
        start = record['postcode_introduced']
        stop = record['postcode_terminated']

        if pd.isna(stop):
            return date >= start
        else:
            return stop > date >= start

    merged['within_dates'] = merged.apply(check_date_within_range, axis=1)
    # Check long's and lat's are close
    def longitudes_and_latitudes_close(record, tol_meters=coord_tol):
        lat1 = record['Latitude']
        long1 = record['Longitude']
        lat2 = record['lat']
        long2 = record['long']

        # If any are invalid, then False
        if any(pd.isna(val) for val in (lat1, long1, lat2, long2)):
            return False
        return geodesic((lat1, long1), (lat2, long2)).meters <= tol_meters

    merged['coordinates_close'] = merged.apply(longitudes_and_latitudes_close, axis=1)

    # Filter down to the validated postcodes
    matched = merged[merged['within_dates'] & merged['coordinates_close']]
    matched = matched[['urn', 'Postcode']]
    matched['validated'] = True

    # Drop address_list's Postcode column, as we will get the one from postcode_reference
    # which definitely won't have stray strings, only Postcodes of NaNs
    address_list = address_list.drop(columns=['Postcode'])

    # Merge
    address_list = address_list.merge(matched, on='urn', how='left')

    # Replace NaNs with False
    def replace_nans(validated):
        if pd.isna(validated):
            return False
        return validated

    address_list['validated'] = address_list['validated'].apply(replace_nans)

    return address_list


def run(address_list_file_path, postcode_reference_file_path, destination_file_path):
    address_list = import_address_list(address_list_file_path)

    postcode_reference = import_postcode_reference(postcode_reference_file_path)

    extended_address_list = create_columns(address_list, postcode_reference)

    extended_address_list.to_csv(destination_file_path, sep='\t', quoting=csv.QUOTE_ALL, index=False)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Missing parameters, please make sure the command conforms to the below shape.")
        print("python pipeline <address_list_file_path> <postcode_reference_file_path> <destination_file_path>")
    else:
        address_list_file_path, postcode_reference_file_path, destination_file_path = sys.argv[1:]

        run(address_list_file_path, postcode_reference_file_path, destination_file_path)
