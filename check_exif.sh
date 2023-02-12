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

GEN_IMAGES_DIR="./generated/images"

echo "Spot check the EXIF metadata summary below"

png_images=()
while IFS= read -r -d $'\0'; do
  png_images+=("$REPLY")
done < <(find -s "$GEN_IMAGES_DIR" -d 1 -type f -name "*.png" -print0)

echo_exif() {
  file_path="$1"
  echo "================="
  echo "EXIF Summary for: $file_path"
  echo "================="
  exiftool -subject -title -author -CreatorWorkEmail -CreatorWorkURL -CreatorCountry -copyright -marked -keywords -description "$file_path"
}

echo
first_png=${png_images[0]}
echo_exif "$first_png"

echo
last_index=$(( ${#png_images[@]} - 1 ))
last_png=${png_images[last_index]}
echo_exif "$last_png"
