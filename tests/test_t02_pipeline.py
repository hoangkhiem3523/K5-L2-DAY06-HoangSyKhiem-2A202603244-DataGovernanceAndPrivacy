"""Unit tests for Track T02 PoC pipeline: camera-aware and lighting-aware triage."""
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import pytest

from src.pipeline import _score_image
from src.common.corruptions import blur, dark, glare, jpeg


def _make_sample_image(tmp_path: Path, filename: str, img_array: np.ndarray) -> Path:
    p = tmp_path / filename
    Image.fromarray(img_array.astype(np.uint8)).save(p, format="JPEG", quality=95)
    return p


def test_t02_clean_day_image_not_defective(tmp_path):
    # Standard day pattern with high detail
    rng = np.random.default_rng(42)
    clean_arr = rng.integers(60, 200, size=(180, 320, 3), dtype=np.uint8)
    p = _make_sample_image(tmp_path, "clean_day.jpg", clean_arr)
    
    res = _score_image(p, camera_id="cam_A", light="day")
    assert res["pred_defect_type"] == "none"
    assert res["pred_action"] == "KEEP"
    assert res["score"] <= 0.3


def test_t02_blur_defect_detected(tmp_path):
    # Highly blurred image
    clean_arr = np.zeros((180, 320, 3), dtype=np.uint8)
    ramp = np.linspace(50, 200, 320, dtype=np.uint8)
    clean_arr[:, :, 0] = ramp
    clean_arr[:, :, 1] = ramp
    clean_arr[:, :, 2] = ramp
    blurred_arr = blur(clean_arr, severity=2)
    p = _make_sample_image(tmp_path, "blur.jpg", blurred_arr)
    
    res = _score_image(p, camera_id="cam_A", light="day")
    assert res["pred_defect_type"] == "blur"
    assert res["pred_action"] == "RECAPTURE"
    assert res["score"] > 0.8


def test_t02_camera_b_soft_lens_not_false_alarm(tmp_path):
    # Camera B has softer lens (laplacian variance ~ 250), ensure it is not falsely flagged as blur
    fx_img = Path("fixtures/t02_raw_qc/images/img_00_0.jpg")
    if fx_img.exists():
        res = _score_image(fx_img, camera_id="cam_B", light="day")
        assert res["pred_defect_type"] == "none"
        assert res["pred_action"] == "KEEP"


def test_t02_clean_night_image_not_flagged_as_dark(tmp_path):
    # Legitimate night image from fixtures (img_01_0) should not be flagged as dark
    fx_night = Path("fixtures/t02_raw_qc/images/img_01_0.jpg")
    if fx_night.exists():
        res = _score_image(fx_night, camera_id="cam_A", light="night")
        assert res["pred_defect_type"] == "none"
        assert res["pred_action"] == "KEEP"


def test_t02_dark_defect_detected(tmp_path):
    # Extreme underexposure (mean < 5)
    dark_arr = np.full((180, 320, 3), 3, dtype=np.uint8)
    p = _make_sample_image(tmp_path, "dark.jpg", dark_arr)
    
    res = _score_image(p, camera_id="cam_A", light="day")
    assert res["pred_defect_type"] == "dark"
    assert res["pred_action"] == "RECAPTURE"
    assert res["score"] > 0.8


def test_t02_extreme_glare_saturation(tmp_path):
    """Edge case: Extreme specular overexposure / whiteout (pixel saturation)."""
    # Create an image with large blown-out saturated glare region (pixels = 255)
    clean_arr = np.full((180, 320, 3), 120, dtype=np.uint8)
    clean_arr[40:140, 80:240, :] = 255  # Overexposed glare spot > 25% area
    p = _make_sample_image(tmp_path, "extreme_glare.jpg", clean_arr)

    res = _score_image(p, camera_id="cam_A", light="day")
    assert res["pred_defect_type"] == "glare"
    assert res["pred_action"] == "RECAPTURE"
    assert res["score"] >= 0.8


def test_t02_border_lighting_condition_dusk(tmp_path):
    """Edge case: Dusk / twilight condition with lower natural contrast should not false-alarm."""
    rng = np.random.default_rng(101)
    # Typical dusk range: mid-tones between 60 and 130 with texture
    dusk_arr = rng.integers(60, 130, size=(180, 320, 3), dtype=np.uint8)
    p = _make_sample_image(tmp_path, "clean_dusk.jpg", dusk_arr)

    res = _score_image(p, camera_id="cam_A", light="dusk")
    assert res["pred_defect_type"] == "none"
    assert res["pred_action"] == "KEEP"
    assert res["score"] <= 0.3


def test_t02_compression_defect_detected(tmp_path):
    """Edge case: Severe JPEG blockiness artifact."""
    clean_arr = np.zeros((180, 320, 3), dtype=np.uint8)
    ramp = np.linspace(40, 220, 320, dtype=np.uint8)
    clean_arr[:, :, 0] = ramp
    clean_arr[:, :, 1] = ramp
    clean_arr[:, :, 2] = ramp
    comp_arr = jpeg(clean_arr, severity=2)
    p = _make_sample_image(tmp_path, "severe_comp.jpg", comp_arr)

    res = _score_image(p, camera_id="cam_A", light="day")
    assert res["pred_defect_type"] == "compression"
    assert res["pred_action"] == "RECAPTURE"
    assert res["score"] > 0.5

