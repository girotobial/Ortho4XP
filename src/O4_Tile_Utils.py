import os
import queue
import shutil
import threading
import time

from . import O4_Mask_Utils as mask
from . import O4_Mesh_Utils as mesh
from . import O4_Overlay_Utils as overlay
from . import O4_UI_Utils as ui
from . import O4_Vector_Map as vmap
from . import dsf, filenames, imagery
from .O4_Parallel_Utils import parallel_join, parallel_launch

max_convert_slots = 4
skip_downloads = False
skip_converts = False

##############################################################################
def download_textures(tile, download_queue, convert_queue):
    ui.vprint(1, "-> Opening download queue.")
    done = 0
    while True:
        texture_attributes = download_queue.get()
        if (
            isinstance(texture_attributes, str)
            and texture_attributes == "quit"
        ):
            ui.progress_bar(2, 100)
            break
        if imagery.build_jpeg_ortho(tile, *texture_attributes):
            done += 1
            ui.progress_bar(
                2, int(100 * done / (done + download_queue.qsize()))
            )
            convert_queue.put((tile, *texture_attributes))
        if ui.red_flag:
            ui.vprint(1, "Download process interrupted.")
            return 0
    if done:
        ui.vprint(1, " *Download of textures completed.")
    return 1


##############################################################################

##############################################################################
def build_tile(tile):
    if ui.is_working:
        return 0
    ui.is_working = 1
    ui.red_flag = False
    ui.logprint(
        "Step 3 for tile lat=", tile.lat, ", lon=", tile.lon, ": starting."
    )
    ui.vprint(
        0,
        "\nStep 3 : Building DSF/Imagery for tile "
        + filenames.short_latlon(tile.lat, tile.lon)
        + " : \n--------\n",
    )

    if not os.path.isfile(
        filenames.mesh_file(tile.build_dir, tile.lat, tile.lon)
    ):
        ui.lvprint(
            0, "ERROR: A mesh file must first be constructed for the tile!"
        )
        ui.exit_message_and_bottom_line("")
        return 0

    timer = time.time()

    tile.write_to_config()

    if not imagery.initialize_local_combined_providers_dict(tile):
        ui.exit_message_and_bottom_line("")
        return 0

    try:
        if not os.path.exists(
            os.path.join(
                tile.build_dir,
                "Earth nav data",
                filenames.round_latlon(tile.lat, tile.lon),
            )
        ):
            os.makedirs(
                os.path.join(
                    tile.build_dir,
                    "Earth nav data",
                    filenames.round_latlon(tile.lat, tile.lon),
                )
            )
        if not os.path.isdir(os.path.join(tile.build_dir, "textures")):
            os.makedirs(os.path.join(tile.build_dir, "textures"))
        if ui.cleaning_level > 1 and not tile.grouped:
            for f in os.listdir(os.path.join(tile.build_dir, "textures")):
                if f[-4:] != ".png":
                    continue
                try:
                    os.remove(os.path.join(tile.build_dir, "textures", f))
                except:
                    pass
        if not tile.grouped:
            try:
                shutil.rmtree(os.path.join(tile.build_dir, "terrain"))
            except:
                pass
        if not os.path.isdir(os.path.join(tile.build_dir, "terrain")):
            os.makedirs(os.path.join(tile.build_dir, "terrain"))
    except Exception as e:
        ui.lvprint(0, "ERROR: Cannot create tile subdirectories.")
        ui.vprint(3, e)
        ui.exit_message_and_bottom_line("")
        return 0

    download_queue = queue.Queue()
    convert_queue = queue.Queue()
    build_dsf_thread = threading.Thread(
        target=dsf.build_dsf, args=[tile, download_queue]
    )
    download_thread = threading.Thread(
        target=download_textures, args=[tile, download_queue, convert_queue]
    )
    build_dsf_thread.start()
    if not skip_downloads:
        download_thread.start()
        if not skip_converts:
            ui.vprint(
                1,
                "-> Opening convert queue and",
                max_convert_slots,
                "conversion workers.",
            )
            dico_conv_progress = {"done": 0, "bar": 3}
            convert_workers = parallel_launch(
                imagery.convert_texture,
                convert_queue,
                max_convert_slots,
                progress=dico_conv_progress,
            )
    build_dsf_thread.join()
    if not skip_downloads:
        download_queue.put("quit")
        download_thread.join()
        if not skip_converts:
            for _ in range(max_convert_slots):
                convert_queue.put("quit")
            parallel_join(convert_workers)
            if ui.red_flag:
                ui.vprint(1, "DDS conversion process interrupted.")
            elif dico_conv_progress["done"] >= 1:
                ui.vprint(1, " *DDS conversion of textures completed.")
    ui.vprint(1, " *Activating DSF file.")
    dsf_file_name = os.path.join(
        tile.build_dir,
        "Earth nav data",
        filenames.long_latlon(tile.lat, tile.lon) + ".dsf",
    )
    try:
        os.rename(dsf_file_name + ".tmp", dsf_file_name)
    except:
        ui.vprint(0, "ERROR : could not rename DSF file, tile is not actived.")
    if ui.red_flag:
        ui.exit_message_and_bottom_line()
        return 0
    if ui.cleaning_level > 1:
        try:
            os.remove(filenames.alt_file(tile))
        except:
            pass
        try:
            os.remove(filenames.input_node_file(tile))
        except:
            pass
        try:
            os.remove(filenames.input_poly_file(tile))
        except:
            pass
    if ui.cleaning_level > 2:
        try:
            os.remove(filenames.mesh_file(tile.build_dir, tile.lat, tile.lon))
        except:
            pass
        try:
            os.remove(filenames.apt_file(tile))
        except:
            pass
    if ui.cleaning_level > 1 and not tile.grouped:
        remove_unwanted_textures(tile)
    ui.timings_and_bottom_line(timer)
    ui.logprint(
        "Step 3 for tile lat=", tile.lat, ", lon=", tile.lon, ": normal exit."
    )
    return 1


##############################################################################

##############################################################################
def build_all(tile):
    vmap.build_poly_file(tile)
    if ui.red_flag:
        ui.exit_message_and_bottom_line("")
        return 0
    mesh.build_mesh(tile)
    if ui.red_flag:
        ui.exit_message_and_bottom_line("")
        return 0
    mask.build_masks(tile)
    if ui.red_flag:
        ui.exit_message_and_bottom_line("")
        return 0
    build_tile(tile)
    if ui.red_flag:
        ui.exit_message_and_bottom_line("")
        return 0
    ui.is_working = 0
    return 1


##############################################################################

##############################################################################
def build_tile_list(
    tile, list_lat_lon, do_osm, do_mesh, do_mask, do_dsf, do_ovl, do_ptc
):
    if ui.is_working:
        return 0
    ui.red_flag = 0
    timer = time.time()
    ui.lvprint(
        0, "Batch build launched for a number of", len(list_lat_lon), "tiles."
    )

    for (k, (lat, lon)) in enumerate(list_lat_lon):
        ui.vprint(
            1,
            "Dealing with tile ",
            k + 1,
            "/",
            len(list_lat_lon),
            ":",
            filenames.short_latlon(lat, lon),
        )
        (tile.lat, tile.lon) = (lat, lon)
        tile.build_dir = filenames.build_dir(
            tile.lat, tile.lon, tile.custom_build_dir
        )
        tile.dem = None
        if do_ptc:
            tile.read_from_config()
        if do_osm or do_mesh or do_dsf:
            tile.make_dirs()
        if do_osm:
            vmap.build_poly_file(tile)
            if ui.red_flag:
                ui.exit_message_and_bottom_line()
                return 0
        if do_mesh:
            mesh.build_mesh(tile)
            if ui.red_flag:
                ui.exit_message_and_bottom_line()
                return 0
        if do_mask:
            mask.build_masks(tile)
            if ui.red_flag:
                ui.exit_message_and_bottom_line()
                return 0
        if do_dsf:
            build_tile(tile)
            if ui.red_flag:
                ui.exit_message_and_bottom_line()
                return 0
        if do_ovl:
            overlay.build_overlay(lat, lon)
            if ui.red_flag:
                ui.exit_message_and_bottom_line()
                return 0
        try:
            ui.gui.earth_window.canvas.delete(
                ui.gui.earth_window.dico_tiles_todo[(lat, lon)]
            )
            ui.gui.earth_window.dico_tiles_todo.pop((lat, lon), None)
        except Exception as e:
            print(e)
    ui.lvprint(
        0, "Batch process completed in", ui.nicer_timer(time.time() - timer)
    )
    return 1


##############################################################################

##############################################################################
def remove_unwanted_textures(tile):
    texture_list = []
    for f in os.listdir(os.path.join(tile.build_dir, "terrain")):
        if f[-4:] != ".ter":
            continue
        if f[-5] != "y":  # overlay
            texture_list.append(f.replace(".ter", ".dds"))
        else:
            texture_list.append("_".join(f[:-4].split("_")[:-2]) + ".dds")
    for f in os.listdir(os.path.join(tile.build_dir, "textures")):
        if f[-4:] != ".dds":
            continue
        if f not in texture_list:
            print("Removing obsolete texture", f)
            try:
                os.remove(os.path.join(tile.build_dir, "textures", f))
            except:
                pass
