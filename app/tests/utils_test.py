from app.utils import compute_crc32


def test_compute_crc32():
    assert compute_crc32("exd") == 3818617241
