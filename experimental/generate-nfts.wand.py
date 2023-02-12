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

# NOTE:
# The Wand implementation was the fastest. OpenCV may be faster but requires more complicated calculations.

import argparse
import os
import time
from wand.image import Image

layer_names = []
layer_dir_files = {}

num_layers = 0
num_generated = 0

layers_dir_path_str = '../layers'
gen_dir_path_str = './generated'


def main():
    parser = argparse.ArgumentParser(
        prog='Generate-NFTs',
        description='Generates NFT composite images from trait files.',
        epilog="Ray Cardillo - Cardillo's Creations")

    parser.add_argument(
        'layers',
        default='./layers',
        help='the layers input directory'
    )
    parser.add_argument(
        'generated',
        default='./generated',
        help='the generated output directory to create'
    )

    args = parser.parse_args()

    global layers_dir_path_str
    layers_dir = args.layers

    global gen_dir_path_str
    gen_dir = args.generated

    global layer_names
    layer_dirs = {}
    for layer_dir in sorted(os.scandir(layers_dir), key=lambda e: e.name):
        if layer_dir.is_dir():
            layer_name = layer_dir.name
            layer_names.append(layer_name)
            layer_dirs[layer_name] = layer_dir

    global num_layers
    num_layers = len(layer_dirs)
    print(f'Discovered {num_layers} Layers:')

    global layer_dir_files
    for layer_name, layer_dir in layer_dirs.items():
        print(f'  {layer_name} = {layer_dir}')

        layer_files = []
        for layer_file in sorted(os.scandir(layer_dir), key=lambda e: e.name):
            print(f'    {layer_file}')
            layer_files.append(layer_file)

        layer_dir_files[layer_dir.name] = layer_files

    print('\nGenerating image combinations...')
    os.makedirs(gen_dir, exist_ok=True)

    walk([])


def generate_image(parts):
    global num_generated
    generated = None

    p_start = time.perf_counter()

    for entry in parts:
        image = Image(filename=entry.path)

        if generated is None:
            generated = image
        else:
            generated.composite(image)

    num_generated += 1
    file_path = os.path.join(gen_dir_path_str, f'{num_generated:05}.png')
    generated.save(filename=file_path)
    generated.close()

    p_stop = time.perf_counter()
    print(f'[{p_stop-p_start:.02f}s] {file_path}')


def walk(parts):
    parts_len = len(parts)
    #print(f'\nWalking parts_len:{parts_len} parts:{parts}')

    global num_layers
    if parts_len == num_layers:
        #print('PARTS:')
        #print(' ', '\n  '.join(map(lambda e: e.name, parts)))
        generate_image(parts)
    else:
        global layer_names, layer_dir_files
        for layer_index in range(parts_len, num_layers):
            layer = layer_names[layer_index]
            layer_files = layer_dir_files[layer]

            for layer_file in layer_files:
                new_parts = parts.copy()
                new_parts.append(layer_file)
                walk(new_parts)


if __name__ == "__main__":
    main()
