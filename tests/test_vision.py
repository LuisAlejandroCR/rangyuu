# test_vision.py: el carril de visión sin descargar el modelo. La sesión ONNX se sustituye por una
# que devuelve detecciones inventadas a propósito, así se prueba la regla —qué cuenta como
# obstáculo, qué como aviso— sin 29 MB de pesos ni una GPU.

import numpy as np
import pytest

from rangyuu.onboard import CLEAR, OBSTACLE, UNCERTAIN
from rangyuu.vision import ModelUnavailable, ObjectEye, Sighting


class FakeSession:
    """Devuelve lo que se le pida, con la forma exacta de SSD MobileNet."""

    def __init__(self, detections):
        self.detections = detections

    def get_inputs(self):
        return [type("I", (), {"name": "image_tensor:0"})()]

    def run(self, _outputs, _feed):
        boxes = np.array([[d[2] for d in self.detections]], dtype=np.float32) if self.detections \
            else np.zeros((1, 0, 4), dtype=np.float32)
        classes = np.array([[d[0] for d in self.detections]], dtype=np.float32)
        scores = np.array([[d[1] for d in self.detections]], dtype=np.float32)
        return boxes, classes, scores, np.array([len(self.detections)], dtype=np.float32)


def eye(detections):
    instance = ObjectEye.__new__(ObjectEye)
    instance.session = FakeSession(detections)
    instance.input_name = "image_tensor:0"
    instance.min_score = 0.45
    instance.last_ms = 0.0
    instance.last_objects = []
    return instance


FRAME = np.zeros((64, 48, 3), dtype=np.uint8)
MOTO_FAR = (4, 0.69, (0.15, 0.40, 0.45, 0.60))        # centrada, lejos: el borde inferior es alto
MOTO_NEAR = (4, 0.80, (0.30, 0.35, 0.85, 0.70))       # centrada y cerca
CHAIR_SIDE = (62, 0.90, (0.40, 0.88, 0.95, 0.99))     # al costado, fuera del corredor
BIRD = (16, 0.99, (0.10, 0.45, 0.20, 0.55))           # no bloquea a nadie


def test_an_empty_frame_is_clear():
    assert eye([]).look(FRAME).state == CLEAR


def test_something_close_in_the_corridor_is_an_obstacle():
    reading = eye([MOTO_NEAR]).look(FRAME)
    assert reading.state == OBSTACLE and reading.confidence == pytest.approx(0.80, abs=0.01)


def test_the_same_thing_far_away_is_a_warning_not_a_stop():
    assert eye([MOTO_FAR]).look(FRAME).state == UNCERTAIN


def test_an_object_outside_the_corridor_does_not_block_the_path():
    assert eye([CHAIR_SIDE]).look(FRAME).state == CLEAR


def test_classes_that_cannot_block_a_walker_are_ignored():
    assert eye([BIRD]).look(FRAME).state == CLEAR


def test_low_scores_are_ignored():
    assert eye([(4, 0.20, (0.3, 0.35, 0.85, 0.7))]).look(FRAME).state == CLEAR


def test_what_was_seen_is_named_so_the_screen_can_say_it():
    described = eye([MOTO_NEAR, CHAIR_SIDE]).describe(FRAME)
    labels = {o["label"] for o in described["objects"]}
    assert labels == {"moto", "silla"}
    assert described["state"] == OBSTACLE and "inference_ms" in described


def test_a_frame_that_is_not_rgb_is_refused():
    with pytest.raises(ValueError):
        eye([]).look(np.zeros((64, 48), dtype=np.uint8))


def test_without_a_model_it_refuses_instead_of_pretending(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("RANGYUU_ONNX_MODEL", raising=False)
    from rangyuu import config
    config.reset()
    with pytest.raises(ModelUnavailable):
        ObjectEye()


def test_the_site_falls_back_and_says_which_detector_it_uses():
    from rangyuu.serve import build_site
    site = build_site()
    assert site.onboard_kind in {"onnx", "texturas"}
    assert site.source_report()["onboard"]["detector"] == site.onboard_kind
