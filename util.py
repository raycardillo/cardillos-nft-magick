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

from dataclasses import dataclass, field
from pathlib import Path

from wand.image import Image


def join_traits(traits: list[str]):
    """
    Join a list of trait JSON dicts to a JSON list of dicts.
    :param traits: list of JSON dict strings.
    :return: final JSON string containing a JSON list of dicts.
    """
    return '[' + ','.join(traits) + ']'


@dataclass(init=False, repr=False, frozen=True)
class Const:
    """
    Common constants used throughout this project.
    """

    DEFAULT_LAYERS_DIR: str = './layers'
    DEFAULT_GEN_DIR: str = './generated'
    GEN_IMAGE_SUBDIR: str = 'images'

    DEFAULT_CSV_FILE_NAME: str = 'assets.csv'

    TRAIT_TRANS = str.maketrans("_-", "  ")

    # This is currently using the NiftyKit DropKit format. I may add support for others in the future.
    # https://docs.niftykit.com/nft-drop-collection/get-started/generating-assets/uploading-your-assets-and-metadata-to-your-drop-collection/csv-json-import-metadata
    CSV_FIELD_NAME = 'name'
    CSV_FIELD_DESC = 'description'
    CSV_FIELD_ATTS = 'attributes'
    CSV_FIELD_IMAGE = 'image'
    CSV_FIELDNAMES = [
        CSV_FIELD_NAME,
        CSV_FIELD_DESC,
        CSV_FIELD_ATTS,
        CSV_FIELD_IMAGE,
        'animation_url',
        'background_color',
        'youtube_url',
        'external_url'
    ]


@dataclass(frozen=True)
class Trait:
    """
    Trait data object.
    """

    type: str
    value: str
    weight: int

    def csv_json(self):
        return f'{{"trait_type":"{self.type}","value":"{self.value}"}}'


@dataclass(frozen=True)
class TraitImageInfo:
    """
    Trait image file info (including the `Trait` data object).
    """

    image: Image
    name: str
    path: str
    trait: Trait


@dataclass
class LayerInfo:
    """
    Layer directory info (including trait images and summary info).
    """

    name: str
    path: Path
    trait_type: str
    total_weight: int
    trait_images: list[TraitImageInfo]
    weights: list[int] = field(init=False, default=None)

    def __post_init__(self):
        self.weights = list(map(lambda ti: ti.trait.weight, self.trait_images))


@dataclass
class GeneratedImageInfo:
    """
    Generated image info containing path and traits string.
    """
    file_name: str
    file_path: str
    traits_str: str
