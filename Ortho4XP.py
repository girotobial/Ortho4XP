#!/usr/bin/env python3
import os
import sys

import src.airport_data as airport_data
import src.filenames as filenames
import src.gui as gui
import src.imagery as image
import src.mask as mask
import src.mesh as mesh
import src.tile as tiles
import src.vector_map as vmap
from src import (
    config,  # CFG imported last because it can modify other modules variables
)

Ortho4XP_dir = os.pardir if getattr(sys, "frozen", False) else os.curdir

cmd_line = (
    "USAGE: Ortho4XP.py lat lon imagery zl (won't read a tile config)\n   OR: "
    " Ortho4XP.py lat lon (with existing tile config file)"
)

if __name__ == "__main__":
    if not os.path.isdir(filenames.Utils_dir):
        print(
            "Missing ",
            filenames.Utils_dir,
            "directory, check your install. Exiting.",
        )
        sys.exit()
    for directory in (
        filenames.Preview_dir,
        filenames.Provider_dir,
        filenames.Extent_dir,
        filenames.Filter_dir,
        filenames.OSM_dir,
        filenames.Mask_dir,
        filenames.Imagery_dir,
        filenames.Elevation_dir,
        filenames.Geotiff_dir,
        filenames.Patch_dir,
        filenames.Tile_dir,
        filenames.Tmp_dir,
        filenames.Airport_dir,
    ):
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
                print("Creating missing directory", directory)
            except OSError:
                print(
                    "Could not create required directory", directory, ". Exit."
                )
                sys.exit()
    image.initialize_extents_dict()
    image.initialize_color_filters_dict()
    image.initialize_providers_dict()
    image.initialize_combined_providers_dict()
    airport_data.AirportDataSource.update_cache()

    if len(sys.argv) == 1:  # switch to the graphical interface
        Ortho4XP = gui.Ortho4XP_GUI()
        Ortho4XP.mainloop()
        print("Bon vol!")

    else:  # sequel is only concerned with command line
        if len(sys.argv) < 3:
            print(cmd_line)
            sys.exit()
        try:
            lat = int(sys.argv[1])
            lon = int(sys.argv[2])
        except ValueError:
            print(cmd_line)
            sys.exit()
        if len(sys.argv) == 3:
            try:
                tile = config.Tile(lat, lon, "")
            except Exception as e:
                print(e)
                print("ERROR: could not read tile config file.")
                sys.exit()
        else:
            try:
                provider_code = sys.argv[3]
                zoomlevel = int(sys.argv[4])
                tile = config.Tile(lat, lon, "")
                tile.default_website = provider_code
                tile.default_zl = zoomlevel
            except:
                print(cmd_line)
                sys.exit()
        try:
            vmap.build_poly_file(tile)
            mesh.build_mesh(tile)
            mask.build_masks(tile)
            tiles.build_tile(tile)
            print("Bon vol!")
        except:
            print("Crash!")
