# test_live.py: the parts of the live receiver that do not need a network — the measured
# report and its arithmetic. Receiving media itself is exercised against Ring, not here.

from rangyuu.live import LiveReport


def test_fps_is_frames_over_the_measured_duration():
    report = LiveReport("d", frames=150, width=1920, height=1080, duration_s=10.0)
    assert report.fps == 15.0
    assert report.as_dict()["resolution"] == "1920x1080"


def test_a_session_without_frames_reports_zero_not_a_guess():
    report = LiveReport("d", duration_s=10.0)
    assert report.fps == 0.0
    assert report.as_dict()["resolution"] is None
    assert report.as_dict()["frames"] == 0


def test_distinct_frames_are_counted_so_a_frozen_stream_is_visible():
    frozen = LiveReport("d", frames=90, duration_s=6.0, frame_hashes=[7, 7, 7, 7])
    moving = LiveReport("d", frames=90, duration_s=6.0, frame_hashes=[1, 2, 3, 4])
    assert frozen.as_dict()["distinct_frames"] == 1
    assert moving.as_dict()["distinct_frames"] == 4
