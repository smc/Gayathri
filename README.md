A new typeface in development. Designer: Binoy Domenic


Building from source
--------------------
1. Install the python libraries required for build script:
    ```
    pip3 install -r requirements.txt
    ```
2. Build the ttf, otf, woff2 files:
   ```
   make all
   ```

Development
-----------
Following development workflow is used for this typeface
1. Designer produces SVG files with correct dimentions in the 2048em size. Commits to the repository
2. Typeface Engineers prepared a big  configuration file containing svg file name to UFO glif mapping. See sources/svg-glif-mapping.yaml. It has left, right bearings, glyph width, base position in em canvas, unicode value and glyph name.
3. Typeface Engineers execute a script `make ufo` to prepare or update the UFO from the svgs.
   1. `Make ufo` first executes tools/import-svg-to-ufo.py to convert the svg to a UFO glif file. It uses the configuration for the svg defined in sources/svg-glif-mapping.yaml
   2. `Make ufo` then executes `ufonormalizer` to clean up the UFO and do various normalization
   3. Finally `ufolint` is executed to lint the UFO.
4. Typeface engineers construct the glyphs that use components(references) using a UFO editor like `trufont`
5. `make otf` Generates the OTF font
6. `make test` Generates a PDF with sample content for manual visual inspection.
7. Webfonts, TTF are also generated.
8. Gitlab CI pipeline executes `make otf ttf webfonts` and uploads the webfonts to a Gitlab pages so that a demo webpage is also prepared. From this pipeline results the generated font can also be downloaded.

License
-------
Licensed under the SIL Open Font License, Version 1.1. http://scripts.sil.org/OFL
