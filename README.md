# cardillos-nft-magick

A collection of handy Python NFT generator helper utilities.


## From the author

>This repo was created specifically to help me when publishing with the [NiftyKit](https://niftykit.com) [DropKit](https://docs.niftykit.com/nft-drop-collection/drop-collection-overview) feature.
>When I started experimenting with generated NFT drops, I couldn't find any [FOSS](https://en.wikipedia.org/wiki/Free_and_open-source_software) utilities that did what I wanted and were simple to use.
>It may be expanded further in the future if there is enough interest, but in the meantime, I'm just putting this out in the wild in case others find it useful as well.
><br/>
>_**Ray Cardillo** (aka, [Cardillo's Art](https://nfts.cardillos.art), [Cardillo's Creations](https://cardilloscreations.com))_


## Prerequisites

These scripts should work on any system that satisfies the basic Python requirements (plus ImageMagick and ExifTool).

I develop and test on macOS using the following toolchain:

- **Python**
  - **[PyCharm CE](https://www.jetbrains.com/pycharm/download/#section=mac)** `2022.3.2`
  - **[Python](https://www.python.org/)** `3.11.1` (installed via `brew install python`)
  - See the [requirements.txt](./requirements.txt) file for package dependencies.
- **Required Libs & Tools**
  - **[ImageMagick](https://imagemagick.org/index.php)** `7.1.0` (installed via `brew install imagemagick`)
  - **[ExifTool](https://exiftool.org/)** `12.50` (installed via `brew install exiftool`)
- _**Optional Libs & Tools**_
  - **[pngcheck](http://www.libpng.org/pub/png/apps/pngcheck.html)** `3.0.3` (optional) (installed via `brew install pngcheck`)
  - **[ipfs-car](https://github.com/web3-storage/ipfs-car)** `0.9.1` (optional) (requires `npm`/`npx` and used via `npx ipfs-car`)


## How To Use

Once you have created your assets and exported them into a `layers` directory,
the overall process of preparing for a drop will look something like this:

- Generate unique composite image permutations and metadata.
- Verify and spot check the images, CSV metadata, and EXIF metadata.
- Upload images to IPFS as a directory and register with a pinning service.
- Update the CSV metadata to add the IPFS directory base URL prefix.
- Use a service such as [NiftyKit](https://niftykit.com) to help publish.

The following is a rough guide about how to do this with the programs in this repo:
1. **[exif_metadata.yaml](./exif_metadata.yaml)**<br/>
   Update the EXIF metadata config YAML file before generating. These values will be used to set the image metadata while generating images.
2. **[generate-nfts.py](./generate_nfts.py)**<br/>
   Analyzes the files in the `layers` directory to generate *composite images* and the initial *assets metadata* CSV file.
   - The `layers` subdirectories are used as the layer names (which are the *trait types* (e.g., Background, Body, Eyes)).
   - The layer directories are prefixed with a number to establish their layering order.
   - The files in each layer directory are alpha composite trait files (which establish the *trait values* (e.g., Red, White, Blue)).
   - The trait image file name should have the layer name followed by the trait value name (e.g., `.../layers/02-LayerName/some-other-stuff-LayerName-TraitName#20.png`)
   - The trait image file name can end with a hash character `#` followed by a number to indicate *trait weight* (otherwise `1` is assumed).
3. **Review & Upload**<br/>
   Review the generated images and metadata. If satisfied, the entire directory will need to be uploaded IPFS so a base URL can be established in the next step (updating the image link in the CSV).
   1. **[check_png.sh](./check_png.sh)**<br/>
      Run this `BASH` script that uses `pngcheck` to validate that the PNG files don't have any corruption.
   2. **[check_exif.sh](./check_exif.sh)**<br/>
      Run this `BASH` script that uses `exiftool` to show a summary of key EXIF metadata to spot check the image metadata.
   3. **Upload to IPFS**
      - **[create_car.sh](./create_car.sh)**<br/>
        This `BASH` script uses `npx ipfs-car` to create a CAR file for upload to a service like [NFT.Storage](https://nft.storage/). However, the web UI is limited to 100mb max.
      - **[NFTUp](https://nft.storage/docs/how-to/nftup/)**<br/>
        This is super convenient because you just drag and drop the `images` folder, and it will do all the uploading for you. This is super convenient when the upload is larger than the 100mb max.
      - **ipfs**<br/>
        You can upload to your own `ipfs` node but then the content will still need to be pinned.
   5. **Pin on IPFS**<br/>
      The files must be **pinned** to make sure the images are kept in IPFS for years to come. Services like [NFT.Storage](https://nft.storage/) and [Piñata](https://pinata.cloud) are common choices.
4. **[update_csv.py](./update_csv.py)**<br/>
   Update the image field in the metadata CSV file by prefixing the IPFS base URL to the image name.
   - It's important to end the base URL with a `/` to designate the directory to append the image name to. Also, most marketplaces seem to prefer an `https://` link to an IPFS gateway instead of an `ipfs://` link.
   - This program also detects (and skips) any duplicate trait rows found. However, duplicates should not be possible if using the corresponding generation program above. It's more of a safeguard.


## Random Generation with Weights

The program supports generating all permutations (in order) but that produces "predictable" results that may not be desired.
Conversely, if a number is provided, it will generate of a subset of the max possible.
Subsets are generated by running random trails with memoization to prevent duplicates.

Here are a few important notes about specifying weights:

1. As mentioned above, the trait image file name can end with a hash character `#` followed by a number to indicate *trait weight* (otherwise `1` is assumed).
2. Weights are ignored if generating all possible permutations.
3. The sum of weights does not have to be `100` but doing this can help make the mental math easier.
4. Random trials will take longer as the number requested approaches the maximum possible.


## Known Limitations

AKA, problems this utility is not *currently* trying to solve.

- **Performance of random trials**<br/>
  See comments about the performance as the number requested approaches the max possible permutations.
  Other strategies may be implemented in the future but this strategy is good for randomness.
  The output will help monitor how long and how many trials each image generation is taking.
  The image isn't created unless it's unique so the worst case for typical collections isn't all that bad
  (e.g., for under 10k collections, only about 2s extra on the worst random case and more typically 100ms or less).
- **Cannot specify trait restrictions**<br/>
  This can be important when one trait obfuscates another (e.g., a hat that covers an earring). For collections that need this, the metadata attribute will be unique but the generated image will not be. This can be handled manually for now but this problem was not in scope for what was currently needed.
- **More automation**<br/>
  There is a lot already being automated but a primary goal is to keep things simple. Also, some file operations can be dangerous (e.g., deleting) or costly (e.g., uploading to a pinning service). More may be added at some point, but only if it can help without causing things to get complicated.