import csv
import pandas as pd
import numpy as np
import datetime as dt
from geopy.distance import geodesic


def read_file(address_list, postcode_reference):
    pass


def import_address_list(file_path):
    pass


def import_postcode_reference(file_path):
    pass


def create_columns(address_list, postcode_reference):
    pass


def run(address_list_file_path, postcode_reference_file_path, destination_file_path):
    address_list = import_address_list(address_list_file_path)

    postcode_reference = import_address_list(postcode_reference_file_path)

    extended_address_list = create_columns(address_list, postcode_reference)

    extended_address_list.to_csv(destination_file_path, sep='\t', quoting=csv.QUOTE_NONE)