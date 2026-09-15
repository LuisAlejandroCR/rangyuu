# live.py: receives the WHEP media itself, so frames are decoded outside the browser.
# It measures what a fixture cannot answer — resolution, fps, time to first frame and how
# long a session lasts. aiortc is imported lazily: the core suite must not depend on it.

import asyncio
import time
from dataclasses import dataclass, field

from .ring_client import RingError
from .whep import WhepClient


@dataclass
class LiveReport:
    """What one live session actually delivered. Every field is measured, never assumed."""

    device_id: str
    frames: int = 0
    width: int = 0
    height: int = 0
    first_frame_s: float | None = None
    duration_s: float = 0.0
    ended_by: str = ""
    frame_hashes: list = field(default_factory=list)

    @property
    def fps(self) -> float:
        return round(self.frames / self.duration_s, 2) if self.duration_s > 0 and self.frames else 0.0

    def as_dict(self) -> dict:
        return {"device_id": self.device_id, "frames": self.frames,
                "resolution": f"{self.width}x{self.height}" if self.width else None,
                "fps": self.fps, "first_frame_s": self.first_frame_s,
                "duration_s": round(self.duration_s, 2), "ended_by": self.ended_by,
                "distinct_frames": len(set(self.frame_hashes))}


async def watch(ring_client, device_id: str, *, seconds: float = 10.0, sample_every: int = 15) -> LiveReport:
    """Open a WHEP session, decode frames for `seconds`, then always close the session."""
    try:
        from aiortc import RTCConfiguration, RTCPeerConnection, RTCSessionDescription
    except ImportError:  # pragma: no cover - depends on the environment
        raise RingError("aiortc is required to receive media; install aiortc") from None

    report = LiveReport(device_id=device_id)
    connection = RTCPeerConnection(RTCConfiguration(iceServers=[]))
    connection.addTransceiver("video", direction="recvonly")
    frames = asyncio.Queue()

    @connection.on("track")
    def _on_track(track):  # pragma: no cover - callback driven by the network
        asyncio.ensure_future(_drain(track, frames))

    whep, session = WhepClient(ring_client), None
    started = time.monotonic()
    try:
        offer = await connection.createOffer()
        await connection.setLocalDescription(offer)
        session = whep.open(device_id, connection.localDescription.sdp)
        await connection.setRemoteDescription(RTCSessionDescription(sdp=session.answer, type="answer"))
        deadline = started + seconds
        while time.monotonic() < deadline:
            try:
                frame = await asyncio.wait_for(frames.get(), timeout=max(0.1, deadline - time.monotonic()))
            except asyncio.TimeoutError:
                break
            if frame is None:
                report.ended_by = "track ended"
                break
            report.frames += 1
            report.width, report.height = frame.width, frame.height
            if report.first_frame_s is None:
                report.first_frame_s = round(time.monotonic() - started, 3)
            if report.frames % sample_every == 1:
                report.frame_hashes.append(hash(frame.to_bytes() if hasattr(frame, "to_bytes")
                                                else frame.to_ndarray(format="gray").tobytes()))
        report.ended_by = report.ended_by or "deadline"
    finally:
        report.duration_s = time.monotonic() - started
        await connection.close()
        if session is not None:
            whep.close(session)
    return report


async def _drain(track, queue):  # pragma: no cover - callback driven by the network
    while True:
        try:
            await queue.put(await track.recv())
        except Exception:
            await queue.put(None)
            return
