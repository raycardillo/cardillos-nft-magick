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
import random
import sys
import time
import datetime

from exif_updater import *
from util import *

layers_dir_path_str = Const.DEFAULT_LAYERS_DIR
gen_dir_path_str = Const.DEFAULT_GEN_DIR
gen_image_dir_path_str = Const.GEN_IMAGE_SUBDIR
gen_image_dir_path = os.path.join(gen_dir_path_str, gen_image_dir_path_str)
assets_csv_file_name = Const.DEFAULT_CSV_FILE_NAME
gen_assets_csv_path = os.path.join(gen_dir_path_str, assets_csv_file_name)

nft_name_prefix = None
nft_description_prefix = None

layers: list[LayerInfo] = []
images: list[TraitImageInfo] = []

num_layers = 0
num_generated = 0
num_to_generate = -1
max_possible = 0
verbose = False

exif_updater = ExifUpdater()


def main():
    main_start = time.perf_counter()

    parser = argparse.ArgumentParser(
        prog='Generate NFTs',
        description='Generates NFT composite images from trait files.',
        epilog="Ray Cardillo - Cardillo's Creations - Cardillo's Art")

    parser.add_argument(
        '-N', '--num',
        dest='num_to_generate',
        type=int,
        default=-1,
        help='number of images to randomly generate; otherwise generate ALL in order'
    )
    parser.add_argument(
        '-V', '--verbose',
        dest='verbose',
        type=bool,
        default=False,
        help='verbose output at the cost of slower run time'
    )
    parser.add_argument(
        'layers_dir',
        default='./layers',
        help='layers input directory'
    )
    parser.add_argument(
        'generated_dir',
        default='./generated',
        help='generated output directory to create'
    )
    parser.add_argument(
        'nft_name_prefix',
        default='#',
        help='CSV metadata image name prefix'
    )
    parser.add_argument(
        'nft_description_prefix',
        default='NFT #',
        help='CSV metadata image description prefix'
    )

    args = parser.parse_args()

    global layers_dir_path_str
    layers_dir_path_str = args.layers_dir

    global gen_dir_path_str, gen_image_dir_path, gen_assets_csv_path
    gen_dir_path_str = args.generated_dir
    gen_image_dir_path = os.path.join(gen_dir_path_str, gen_image_dir_path_str)
    gen_assets_csv_path = os.path.join(gen_dir_path_str, assets_csv_file_name)

    global nft_name_prefix, nft_description_prefix
    nft_name_prefix = args.nft_name_prefix
    nft_description_prefix = args.nft_description_prefix

    global num_to_generate
    num_to_generate = args.num_to_generate

    global verbose
    verbose = args.verbose

    for layer_dir in sorted(os.scandir(layers_dir_path_str), key=lambda ld: ld.name):
        if layer_dir.is_dir():
            layer_dir_name = layer_dir.name
            print(f'\nFinding trait images in: {layer_dir_name}')

            layer_trait_type = layer_dir_name[(layer_dir_name.find('-') + 1):]

            total_trait_weight = 0

            trait_images: list[TraitImageInfo] = []
            for layer_file in sorted(os.scandir(layer_dir), key=lambda lf: lf.name):
                layer_file_name = layer_file.name
                print(f'  {layer_file_name}')

                layer_trait_value_start = layer_file_name.find(layer_trait_type) + len(layer_trait_type) + 1
                layer_trait_value_period_index = layer_file_name.rfind('.', layer_trait_value_start)
                layer_trait_value_end = layer_trait_value_period_index

                layer_trait_value_weight_index = \
                    layer_file_name.rfind('#', layer_trait_value_start, layer_trait_value_end)
                layer_trait_weight = 1
                if layer_trait_value_weight_index != -1:
                    layer_trait_value_end = layer_trait_value_weight_index
                    try:
                        layer_trait_weight = \
                            int(layer_file_name[layer_trait_value_weight_index + 1:layer_trait_value_period_index])
                    except ValueError:
                        pass

                total_trait_weight = total_trait_weight + layer_trait_weight

                layer_trait_value = \
                    layer_file_name[layer_trait_value_start:layer_trait_value_end].translate(Const.TRAIT_TRANS)

                layer_trait = Trait(
                    type=layer_trait_type,
                    value=layer_trait_value,
                    weight=layer_trait_weight
                )
                print(f'    {layer_trait}')

                trait_images.append(TraitImageInfo(
                    image=Image(filename=layer_file.path),
                    name=layer_file_name,
                    path=layer_file.path,
                    trait=layer_trait
                ))

            layer_info = LayerInfo(
                name=layer_dir.name,
                path=layer_dir.path,
                trait_type=layer_trait_type,
                trait_images=trait_images,
                total_weight=total_trait_weight
            )
            print(f'  Total layer weight = {layer_info.total_weight}')

            layers.append(layer_info)

    global num_layers
    num_layers = len(layers)
    print(f'\nLayers discovered: {num_layers}')

    global max_possible
    max_possible = 1
    for layer in layers:
        max_possible *= len(layer.trait_images)
    print(f'Max possible permutations: {max_possible}\n')

    if num_to_generate > max_possible:
        print(f'Cannot request more unique images [{num_to_generate}] than the max possible [{max_possible}]')
        sys.stdout.flush()
        exit(1)

    # Deleting content can cause data loss (e.g., if the wrong dir is passed in).
    # Just warn the user, so they can move or delete the directory themselves.
    try:
        os.makedirs(gen_image_dir_path, exist_ok=False)
    except OSError as e:
        print(f'Generated directory already exists or other OS error encountered:')
        print('  ' + e.strerror)
        sys.stdout.flush()
        exit(2)

    with open(gen_assets_csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=Const.CSV_FIELDNAMES)
        csvwriter.writeheader()

        if num_to_generate > 0:
            print(f'Generating [{num_to_generate}] image permutations...')
            generate_weighted_images(csvwriter)
        else:
            print('Generating ALL image permutations...')
            generate_all_images(csvwriter, [])

    print(f'\nGENERATED: {num_generated}')

    total_time = time.perf_counter() - main_start
    hms_time = str(datetime.timedelta(seconds=total_time))
    print(f'TOTAL TIME: {total_time:.03f}s == ({hms_time})hms')


def generate_image(csvwriter, parts):
    """
    Generate a composite image from multiple parts and append metadata to the CSV file.
    :param csvwriter: writer to use when appending rows into the metadata CSV.
    :param parts: image parts to use when generating image.
    :return: `None` if processing should not continue; generated file path otherwise.
    """

    global num_generated, num_to_generate
    if 0 < num_to_generate <= num_generated:
        return None

    generated = None

    p_start = time.perf_counter()

    traits: list[str] = []
    for image_part in parts:
        traits.append(image_part.trait.csv_json())

        # grab the cached part image first
        image = image_part.image

        if generated is None:
            # start with a copy of the cached image
            generated = Image(image)
        else:
            # composite the cached image over the current image
            generated.composite(image)

    num_generated += 1
    file_name = f'{num_generated:05}.png'
    file_path = os.path.join(gen_image_dir_path, file_name)
    generated.save(filename=file_path)
    generated.close()

    image_name = f'{nft_name_prefix}{num_generated}'
    image_desc = f'{nft_description_prefix}{num_generated}'
    traits_str = join_traits(traits)

    while not os.path.exists(file_path):
        time.sleep(.1)

    exif_updater.update_metadata(
        file_path=file_path,
        file_name=file_name,
        image_name=image_name,
        image_desc=image_desc,
        traits_str=traits_str
    )

    p_stop = time.perf_counter()
    print(f'[{p_stop - p_start:.03f}s] {file_path}')
    if verbose:
        print(str(traits))

    csvwriter.writerow({
        Const.CSV_FIELD_NAME: image_name,
        Const.CSV_FIELD_DESC: image_desc,
        Const.CSV_FIELD_IMAGE: file_name,
        Const.CSV_FIELD_ATTS: traits_str
    })

    return GeneratedImageInfo(file_name, file_path, traits_str)


def generate_all_images(csvwriter, parts):
    """
    Recursively generate all permutations of images possible (using :py:func:`generate_image`).
    Note that the image numbers will be "predictable" because they're generated in the order of traversal.
    :param csvwriter: writer to use when appending rows into the metadata CSV.
    :param parts: image parts to use when generating image (use `[]` for initial call).
    :return: `True` if processing should continue; `False` otherwise
    """

    parts_len = len(parts)

    global num_layers
    if parts_len == num_layers:
        return generate_image(csvwriter, parts) is not None
    else:
        global layers
        for layer_index in range(parts_len, parts_len + 1):
            layer_info = layers[layer_index]
            layer_images = layer_info.trait_images
            new_parts = parts.copy()
            for layer_image in layer_images:
                new_parts.append(layer_image)
                if not generate_all_images(csvwriter, new_parts):
                    return False
                new_parts.pop()

    return True


def generate_weighted_images(csvwriter):
    """
    Randomly generate permutations of images using trait value weights (using :py:func:`generate_image`).
    Note that the image numbers will be "unpredictable" because the permutations are randomly generated.
    Also note that it will not generate duplicates but large sets may take a little more time to generate.
    :param csvwriter: writer to use when appending rows into the metadata CSV.
    """

    # NOTE:
    # This is a currently a "brute force" random trials algorithm with memoization to eliminate duplicates.
    # So it will get slower as the number generated approaches the total possible in the collection.
    # The output will help monitor how long and how many trials each image generation is taking.

    trials = 0
    p_last = time.perf_counter()
    memo: set[str] = set()

    global num_generated
    while num_generated < num_to_generate:
        trials += 1
        parts = []
        for layer_index in range(0, num_layers):
            layer_info = layers[layer_index]
            layer_image = random.choices(
                population=layer_info.trait_images,
                weights=layer_info.weights,
                k=1
            )[0]
            parts.append(layer_image)

        # use the traits string to establish a hash string for the memo set
        traits = list(map(lambda ti: ti.trait.csv_json(), parts))
        traits_str = join_traits(traits)

        # only generate if we haven't encountered this combination of traits yet
        if traits_str not in memo:
            gen_info = generate_image(csvwriter, parts)
            file_path = gen_info.file_path
            if file_path is not None:
                # generated a valid image file so add to memo and reset counters
                memo.add(traits_str)

                p_now = time.perf_counter()
                print(f'[{p_now - p_last:.03f}s] random trials: {trials}')
                p_last = p_now

                trials = 0


if __name__ == '__main__':
    main()
