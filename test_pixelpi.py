"""Runnable check for pixelpi.py's SPI byte layout.

Run with: python3 test_pixelpi.py
Needs Pillow (the driver imports it). Each mode writes to a temp file via
--spi_dev, so no hardware is touched. Bounded modes are killed after 0.6s
and their output must be a whole number of frames.
"""

import os
import subprocess
import sys
import tempfile
import time

try:
    from PIL import Image
except ImportError:
    print("SKIP: Pillow not installed")
    sys.exit(0)

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVER = os.path.join(HERE, "pixelpi.py")


def run(args, seconds=None):
    """Run one mode into a temp SPI file, return its bytes."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    cmd = [sys.executable, DRIVER] + args + ["--spi_dev", path]
    if seconds is None:
        subprocess.run(cmd, check=True, cwd=HERE, stdout=subprocess.DEVNULL)
    else:
        proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL)
        time.sleep(seconds)
        proc.terminate()
        proc.wait()
    with open(path, "rb") as f:
        return f.read()


def fails(args):
    """Run one mode that is expected to stop with an error; return its exit code."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    cmd = [sys.executable, DRIVER] + args + ["--spi_dev", path]
    return subprocess.run(cmd, cwd=HERE, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT).returncode


def check(output, label):
    try:
        output()
    except AssertionError as exc:
        print("FAIL %s: %s" % (label, exc))
        return False
    print("ok   %s" % label)
    return True


results = []


def test_all_off_ws2801():
    data = run(["all_off", "--num_leds", "3"])
    assert len(data) == 3 * 3 + 3, len(data)
    assert set(data) == {0}, set(data)


def test_all_on_ws2801():
    data = run(["all_on", "--num_leds", "2"])
    assert len(data) == 2 * 3 + 3, len(data)
    assert list(data[:6]) == [255] * 6, list(data[:6])
    assert list(data[6:]) == [0, 0, 0], list(data[6:])


def test_all_off_sm16716():
    data = run(["all_off", "--chip", "SM16716", "--num_leds", "3"])
    assert len(data) == 50 + 3 * 4, len(data)
    assert list(data[:50]) == [0] * 50
    assert list(data[50:]) == [1] * 12, list(data[50:])


def test_chase_sm16716_frame_size():
    data = run(["chase", "--chip", "SM16716", "--num_leds", "4",
                "--refresh_rate", "50"], seconds=0.6)
    # Frame is 50-byte preamble + 4 bytes per LED. Old code emitted 4n+4
    # pixels' worth (one phantom pixel past the strip), so this catches it.
    assert data and len(data) % (50 + 4 * 4) == 0, len(data)


def test_array_maps_pixels():
    path = os.path.join(tempfile.gettempdir(), "pp_red7.png")
    Image.new("RGB", (7, 7), (255, 0, 0)).save(path)
    data = run(["array", "--filename", path, "--array_width", "7",
                "--array_height", "7"])
    assert len(data) == 49 * 3 + 1, len(data)
    assert list(data[:3]) == [255, 0, 0], list(data[:3])
    assert all(data[i * 3:i * 3 + 3] == b"\xff\x00\x00" for i in range(49))


def test_strip_sm16716_stride():
    path = os.path.join(tempfile.gettempdir(), "pp_sm2.png")
    im = Image.new("RGB", (2, 2))
    im.putpixel((0, 0), (10, 20, 30))
    im.putpixel((0, 1), (40, 50, 60))
    im.putpixel((1, 0), (1, 2, 3))
    im.putpixel((1, 1), (4, 5, 6))
    im.save(path)
    data = run(["strip", "--chip", "SM16716", "--filename", path,
                "--array_height", "2"], seconds=0.6)
    assert data and len(data) % 58 == 0, len(data)
    # 50-byte SM16716 preamble, then 4 bytes per pixel: ON, R, G, B.
    assert list(data[50:58]) == [1, 10, 20, 30, 1, 40, 50, 60], list(data[50:58])


def test_array_uses_16x10_map():
    # pixel_map_16x10.csv must be picked automatically for a 16x10 array.
    data = run(["array", "--filename", os.path.join(HERE, "images", "smiley_16x10.png"),
                "--array_width", "16", "--array_height", "10"])
    assert len(data) == 16 * 10 * 3 + 1, len(data)


def test_wrong_map_size_stops():
    # 9x7 has no dedicated map and pixel_map.csv is 7x7, so it must exit non-zero.
    path = os.path.join(tempfile.gettempdir(), "pp_wide9.png")
    Image.new("RGB", (9, 7), (0, 0, 0)).save(path)
    code = fails(["array", "--filename", path, "--array_width", "9",
                  "--array_height", "7"])
    assert code != 0, code


def test_point_outside_image_stops():
    path = os.path.join(tempfile.gettempdir(), "pp_tiny4.png")
    Image.new("RGB", (4, 4), (0, 0, 0)).save(path)
    code = fails(["array", "--filename", path, "--array_width", "7",
                  "--array_height", "7"])
    assert code != 0, code


for fn in (test_all_off_ws2801, test_all_on_ws2801, test_all_off_sm16716,
           test_chase_sm16716_frame_size, test_array_maps_pixels,
           test_strip_sm16716_stride, test_array_uses_16x10_map,
           test_wrong_map_size_stops, test_point_outside_image_stops):
    results.append(check(fn, fn.__name__))

print("\n%d/%d passed" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
