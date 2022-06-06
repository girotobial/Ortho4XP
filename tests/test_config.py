"""Tests for the new config framework"""

import pytest
from hypothesis import given
from hypothesis.strategies import booleans, complex_numbers, integers, text

from src import config


class TestAppConfig:
    def test_init_with_defaults(self):
        cfg = config.AppConfig()
        assert cfg.verbosity == 1
        assert cfg.cleaning_level == 1
        assert cfg.overpass_server_choice == "random"
        assert not cfg.skip_downloads
        assert not cfg.skip_converts
        assert cfg.max_convert_slots == 4
        assert cfg.check_tms_response
        assert cfg.http_timeout == 10
        assert cfg.max_connect_retries == 5
        assert cfg.max_baddata_retries == 5
        assert cfg.ovl_exclude_pol == [0]
        assert cfg.ovl_exclude_net == []
        assert cfg.xplane_install_dir == "<X-Plane Top Level directory>"
        assert cfg.custom_overlay_src == ""
        assert cfg.apt_smoothing_pix == 8
        assert cfg.road_level == 1
        assert cfg.road_banking_limit == 0.5
        assert cfg.lane_width == 5
        assert cfg.max_levelled_segs == 100000
        assert cfg.water_simplification == 0
        assert cfg.min_area == 0.001
        assert cfg.max_area == 200
        assert cfg.clean_bad_geometries
        assert cfg.mesh_zl == 19

    @given(integers(0, 3))
    def test_verbosity_validation_passes(self, value):
        cfg = config.AppConfig()
        cfg.verbosity = value
        assert cfg.verbosity == value
        cfg2 = config.AppConfig(value)
        assert cfg2.verbosity == value

    @given(integers().filter(lambda n: n > 3 or n < 0))
    def test_verbosity_validation_fails(self, value):
        with pytest.raises(ValueError):
            cfg = config.AppConfig()
            cfg.verbosity = value
        with pytest.raises(ValueError):
            config.AppConfig(verbosity=value)

    @given(integers(0, 3))
    def test_cleaning_level_validation_passes(self, value: int):
        cfg = config.AppConfig()
        cfg.cleaning_level = value
        assert cfg.cleaning_level == value
        cfg2 = config.AppConfig(cleaning_level=value)
        assert cfg2.cleaning_level == value

    @given(integers().filter(lambda n: n > 3 or n < 0))
    def test_cleaning_level_validation_fails(self, value):
        with pytest.raises(ValueError):
            cfg = config.AppConfig()
            cfg.cleaning_level = value
        with pytest.raises(ValueError):
            config.AppConfig(cleaning_level=value)

    @given(booleans())
    def test_booleans_validation_passes(self, value):
        cfg = config.AppConfig(
            skip_downloads=value,
            skip_converts=value,
            check_tms_response=value,
            clean_bad_geometries=value,
        )
        assert cfg.skip_converts == value
        assert cfg.skip_downloads == value
        assert cfg.check_tms_response == value
        assert cfg.clean_bad_geometries == value

        cfg2 = config.AppConfig()
        cfg2.skip_converts = value
        cfg2.skip_downloads = value
        cfg2.check_tms_response = value
        cfg2.clean_bad_geometries = value
        assert cfg2.skip_converts == value
        assert cfg2.skip_downloads == value
        assert cfg2.check_tms_response == value
        assert cfg2.clean_bad_geometries == value

    @given(text())
    def test_booleans_validation_fails(self, value):
        with pytest.raises(ValueError):
            config.AppConfig(
                skip_downloads=value,
                skip_converts=value,
                check_tms_response=value,
                clean_bad_geometries=value,
            )
        with pytest.raises(ValueError):
            cfg = config.AppConfig()
            cfg.skip_converts = value
            cfg.skip_downloads = value
            cfg.check_tms_response = value
            cfg.clean_bad_geometries = value


class TestConfigClass:
    def test_init_with_defaults(self):
        cfg = config.Config()
        assert cfg.app == config.AppConfig()
        assert cfg.curvature_tol == float(2)
        assert cfg.apt_curv_tol == 0.5
        assert cfg.apt_curv_ext == 0.5
        assert cfg.coast_curv_tol == 1
        assert cfg.coast_curv_ext == 0.5
        assert cfg.limit_tris == 0
        assert cfg.hmin == 0
        assert cfg.min_angle == 10
        assert cfg.sea_smoothing_mode == "zero"
        assert cfg.water_smoothing == 10
        assert cfg.iterate == 0
        assert cfg.mask_zl == 14
        assert cfg.masks_width == 100
        assert cfg.masking_mode == "sand"
        assert not cfg.use_masks_for_inland
        assert not cfg.imprint_masks_to_dds
        assert not cfg.masks_use_dem_too
        assert cfg.masks_custom_extent == ""
        assert cfg.default_website == ""
        assert cfg.default_zl == 16
        assert cfg.zone_list == []
        assert cfg.cover_airports_with_highres == "False"
        assert cfg.cover_extent == 1
        assert cfg.cover_zl == 18
        assert cfg.cover_screen_res == "HD_1080p"
        assert cfg.cover_fov == 60.0
        assert cfg.cover_fpa == 10
        assert cfg.cover_greediness == 1
        assert cfg.cover_greediness_threshold == 0.7
        assert cfg.sea_texture_blur == 0
        assert not cfg.add_low_res_sea_ovl
        assert cfg.experimental_water == 0
        assert cfg.ratio_water == 0.25
        assert cfg.normal_map_strength == 1
        assert cfg.terrain_casts_shadows
        assert cfg.overlay_lod == 25000
        assert cfg.custom_dem == ""
        assert cfg.fill_nodata
