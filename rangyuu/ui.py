# ui.py: the four states the screen shows, derived from the three the core decides.
# CUIDADO is not a new decision: it is PROCEED with a thin margin, and it may never
# soften a HOLD. The reason strings live here too, so the screen invents nothing.

from dataclasses import dataclass

CONFIDENCE_MARGIN = 0.15   # above the policy threshold, still counts as thin
FRESHNESS_MARGIN = 0.3     # fraction of max_age left before the observation is "about to expire"

AVANZA = "AVANZA"
CUIDADO = "CUIDADO"
PARA = "PARA"
SIN_CERTEZA = "SIN CERTEZA"

REASONS = {
    "clear high-confidence path": "camino libre",
    "path occupied": "algo ocupa el camino",
    "trajectory unknown": "zona sin cobertura",
    "cell stale": "la observación caducó",
    "camera offline": "cámara sin conexión",
    "session unavailable": "sesión de video caída",
    "homography invalid/derived": "calibración no válida",
    "low confidence": "confianza baja",
    "confidence missing": "sin confianza declarada",
    "evidence missing": "sin evidencia que anclar",
    "contradiction": "el evento contradice el frame",
    "feed stale: no frame within the declared window": "hace rato que no llega imagen",
}


@dataclass(frozen=True)
class Screen:
    """What the main screen shows: one state, one short reason, and why it was softened."""

    state: str
    reason: str
    authorizes: bool
    detail: str = ""

    def as_dict(self) -> dict:
        return {"state": self.state, "reason": self.reason,
                "authorizes": self.authorizes, "detail": self.detail}


def to_screen(report: dict, *, confidence=None, age_fraction=None, adjacent_occupied=False,
              onboard=None) -> Screen:
    """Map one decision report to the screen state.

    `confidence` is the minimum confidence along the path, `age_fraction` how much of the
    freshness window has been used (0 just observed, 1 expired). Both are optional: without
    them a PROCEED stays AVANZA, because a missing input may never invent CUIDADO.
    """
    decision = str(report.get("decision", "UNKNOWN"))
    reason = REASONS.get(str(report.get("reason", "")), str(report.get("reason", "")))

    if decision == "HOLD":
        return Screen(PARA, reason, False)
    if decision != "PROCEED":
        return Screen(SIN_CERTEZA, reason, False)

    # El carril de a bordo es contexto: puede degradar, nunca autorizar por sí solo.
    if onboard == "OBSTACLE":
        return Screen(PARA, "la cámara a bordo ve algo al frente", False,
                      "el mapa autorizaba; la vista a bordo no")
    thin = []
    if onboard == "UNCERTAIN":
        thin.append("la cámara a bordo no puede afirmar qué hay al frente")
    if adjacent_occupied:
        thin.append("hay algo ocupado al lado del camino")
    if confidence is not None and confidence < 0.5 + CONFIDENCE_MARGIN:
        thin.append("la confianza está cerca del umbral")
    if age_fraction is not None and age_fraction > 1.0 - FRESHNESS_MARGIN:
        thin.append("la observación está por caducar")

    if thin:
        return Screen(CUIDADO, reason, True, "; ".join(thin))
    return Screen(AVANZA, reason, True)
