#  Copyright 2023 Raymond Cardillo of Cardillo's Creations.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse
import csv
import os
import sys
import urllib.parse

from util import *

gen_dir_path_str = Const.DEFAULT_GEN_DIR
assets_csv_file_name = Const.DEFAULT_CSV_FILE_NAME
gen_assets_csv_path = os.path.join(gen_dir_path_str, assets_csv_file_name)


def main():
    parser = argparse.ArgumentParser(
        prog='Update CSV',
        description='Checks for duplicates and updates the metadata CSV image links.',
        epilog="Ray Cardillo - Cardillo's Creations - Cardillo's Art")

    parser.add_argument(
        'generated_dir',
        default='./generated',
        help='generated output directory to create'
    )
    parser.add_argument(
        'image_url_base',
        help='CSV metadata image URL base'
    )

    args = parser.parse_args()

    global gen_dir_path_str, gen_assets_csv_path
    gen_dir_path_str = args.generated_dir
    gen_assets_csv_path = os.path.join(gen_dir_path_str, assets_csv_file_name)
    gen_new_assets_csv_path = os.path.join(gen_dir_path_str, assets_csv_file_name + '.new.csv')

    image_url_base = args.image_url_base

    unique_rows: set[str] = set()
    duplicate_rows: list[dict] = list()
    with open(gen_assets_csv_path, 'r', newline='') as assets_csv:
        csvreader = csv.DictReader(assets_csv, fieldnames=Const.CSV_FIELDNAMES)
        with open(gen_new_assets_csv_path, 'w', newline='') as new_assets_csv:
            csvwriter = csv.DictWriter(new_assets_csv, fieldnames=Const.CSV_FIELDNAMES)

            # write the header
            csvwriter.writerow(next(csvreader))

            # iterate over the remaining rows
            rows_read = 0
            for row in csvreader:
                rows_read += 1

                traits_str = row[Const.CSV_FIELD_ATTS]
                if traits_str in unique_rows:
                    duplicate_rows.append(row)
                else:
                    unique_rows.add(traits_str)
                    row[Const.CSV_FIELD_IMAGE] = urllib.parse.urljoin(image_url_base, row[Const.CSV_FIELD_IMAGE])
                    csvwriter.writerow(row)

                sys.stdout.write('.')
                if rows_read % 80 == 0:
                    sys.stdout.write('\n')
                    sys.stdout.flush()

    if rows_read % 80 != 0:
        sys.stdout.write('\n')

    print(f'\nUpdated rows and created new CSV:\n   {gen_new_assets_csv_path}\n')

    print(f'Total rows read from CSV:  {rows_read:5}')
    print(f'Unique rows updated:       {len(unique_rows):5}')

    num_duplicate_rows = len(duplicate_rows)
    print(f'Duplicate rows skipped:    {num_duplicate_rows:5}')

    if num_duplicate_rows > 0:
        print('\nDuplicate rows:')
        for row in duplicate_rows:
            print(
                f'  name: "{row[Const.CSV_FIELD_NAME]}" , image: "{row[Const.CSV_FIELD_IMAGE]}" , atts: "{row[Const.CSV_FIELD_ATTS]}"')


if __name__ == '__main__':
    main()
