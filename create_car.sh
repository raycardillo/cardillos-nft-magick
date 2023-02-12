#!/bin/bash

#
# Copyright 2023 Raymond Cardillo of Cardillo's Creations.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# exit early if any failures happen
set -e
set -o pipefail

GEN_DIR="./generated"
GEN_IMAGES_DIR="$GEN_DIR/images"
CAR_FILE="images.car"

# this script uses ipfs-car to create a CAR file
# https://github.com/web3-storage/ipfs-car
echo "Checking for ipfs-car installation..."
NPX_VERSION=$(npx --yes ipfs-car --version)

version_greater_equal()
{
    printf '%s\n%s\n' "$2" "$1" | sort --check=quiet --version-sort
}

# the version command above should install ipfs-car when prompted
if version_greater_equal "${NPX_VERSION}" 0.9.1
then
  echo "ipfs-car requirement was satisfied"
else
  die "ipfs-car 0.9.1 or above is required"
fi

echo
echo "Creating CAR from images directory..."
npx --yes ipfs-car --pack "$GEN_IMAGES_DIR" --output "$GEN_DIR/$CAR_FILE"
ls -o ./generated/images.car | cut -w -f 4-

echo
echo "Creating CAR catalog file..."
npx --yes ipfs-car --list-full "$GEN_DIR/$CAR_FILE" > "$GEN_DIR/$CAR_FILE.cids"
echo "Created: $GEN_DIR/$CAR_FILE.cids"

echo
echo "IPFS base URL example:"
IPFS_BASE_DIR=$(dirname `tail -1 "$GEN_DIR/$CAR_FILE.cids" | cut -w -f 2-`)
echo "https://ipfs.io/ipfs/$IPFS_BASE_DIR/"

echo
echo "DONE"
