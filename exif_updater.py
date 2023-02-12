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

import yaml
from yaml import SafeLoader
from exiftool import ExifTool


class ExifUpdater:
    def __init__(self):
        with open('exif_metadata.yaml', 'r') as exif_config_file:
            self.data = yaml.load(exif_config_file, Loader=SafeLoader)

        subject = self.data['subject']
        contact = self.data['contact']
        author = contact['author']
        email = contact['email']
        url = contact['url']
        country = contact['country']
        country_name = country['name']
        country_code = country['code']
        image_copyright = self.data['copyright']

        common_args = [
            '-overwrite_original',
            f'-subject={subject}',
            f'-author={author}',
            f'-artist={author}',
            f'-creator={author}',
            f'-CreatorWorkEmail={email}',
            f'-CreatorWorkURL={url}',
            f'-CreatorCountry={country_name}',
            f'-CountryCode={country_code}',
            f'-copyright={image_copyright}',
            '-marked=True'
        ]

        keywords = self.data['keywords']
        for keyword in keywords:
            common_args.append(f'-keywords={keyword}')

        self.exiftool = ExifTool(common_args=common_args)
        self.exiftool.run()

    def __del__(self):
        self.exiftool.terminate()

    def update_metadata(self, file_path, file_name, image_name, image_desc, traits_str):
        details = image_desc + ' :: ' + traits_str
        self.exiftool.execute(
            f'-comment={details}',
            f'-title={image_desc}',
            f'-description={details}',
            file_path
        )
        # print(self.exiftool.last_stderr)
