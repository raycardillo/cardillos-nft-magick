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

echo "Checking generated PNG images for corruption..."

bad_pngs=""
for file in $GEN_IMAGES_DIR/*.png
do
  result=$(pngcheck "$file")
  if [[ $result == OK:* ]]
  then
    echo -n "."
  else
    echo -n "X"
    bad_pngs+="$result"
  fi
done
echo

echo
if [[ -n "$bad_pngs" ]]
then
  echo "Bad PNGs files were discovered:"
  echo "$bad_pngs"
  exit 1 
else
  echo "No bad PNGs files were discovered."
fi
