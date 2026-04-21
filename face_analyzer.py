import base64
import csv
import io
import json
import os
import queue
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

# ── Module-level shared state ─────────────────────────────────────────────────
output_frame: np.ndarray | None = None
frame_lock = threading.Lock()
frame_queue: queue.Queue = queue.Queue(maxsize=1)

# Current detected faces (rebuilt each processed frame)
current_faces: list[dict] = []
current_faces_lock = threading.Lock()


# ═════════════════════════════════════════════════════════════════════════════
# FaceAnalyzer
# ═════════════════════════════════════════════════════════════════════════════

class FaceAnalyzer:
    """Handles recognition, enrollment, sessions, and persistence."""

    THRESHOLD: float = 0.5

    def __init__(
        self,
        model_name: str = "buffalo_l",
        ctx_id: int = 0,
        det_size: tuple = (320, 320),
        data_dir: str = "Face_Attendance_Web_App/known_faces",
        sessions_dir: str = "Face_Attendance_Web_App/sessions",
    ):
        self.app = FaceAnalysis(name=model_name, allowed_modules=["detection", "recognition"])
        self.app.prepare(ctx_id=ctx_id, det_size=det_size)

        self.data_dir = Path(os.path.abspath(data_dir))

        print("data dir:", self.data_dir)

        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_dir = Path(os.path.abspath(sessions_dir))
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "known_faces.json"
        self.sessions_path = self.sessions_dir / "sessions.json"

        self._lock = threading.Lock()

        # {person_id: {"name": str, "enrolled_at": str, "embeddings": [np.ndarray, ...]}}
        self.known_faces: dict = {}
        self._session: dict | None = None     # currently active session
        self._sessions: list[dict] = []       # completed sessions

        self._load_database()
        self._load_sessions()

    # ── Similarity ────────────────────────────────────────────────────────────

    @staticmethod
    def _cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        return float(np.dot(v1, v2) / denom) if denom > 0 else 0.0

    # ── Recognition ───────────────────────────────────────────────────────────

    def recognize(self, embedding: np.ndarray) -> tuple[str, str, float]:
        """
        Returns (person_id, name, best_score).
        person_id == 'unknown' when no match exceeds the threshold.
        """
        best_pid, best_name, best_score = "unknown", "Unknown", 0.0
        with self._lock:
            for pid, data in self.known_faces.items():
                for known_emb in data["embeddings"]:
                    score = self._cosine_similarity(embedding, known_emb)
                    if score > best_score:
                        best_score, best_pid, best_name = score, pid, data["name"]
        if best_score >= self.THRESHOLD:
            return best_pid, best_name, best_score
        return "unknown", "Unknown", best_score

    # ── Enrollment ────────────────────────────────────────────────────────────

    def enroll_from_embedding(self, person_id: str, name: str, embedding: np.ndarray) -> bool:
        """Add an embedding to the database for person_id."""
        with self._lock:
            if person_id not in self.known_faces:
                self.known_faces[person_id] = {
                    "name": name,
                    "enrolled_at": datetime.now(timezone.utc).isoformat(),
                    "embeddings": [],
                }
            self.known_faces[person_id]["embeddings"].append(embedding.copy())
        self._save_database()
        return True

    def rename_person(self, person_id: str, new_name: str) -> bool:
        with self._lock:
            if person_id not in self.known_faces:
                return False
            self.known_faces[person_id]["name"] = new_name
        self._save_database()
        return True

    def delete_person(self, person_id: str) -> bool:
        with self._lock:
            if person_id not in self.known_faces:
                return False
            del self.known_faces[person_id]
        self._save_database()
        return True

    def clear_database(self) -> bool:
        with self._lock:
            self.known_faces.clear()
        self._save_database()
        return True

    def list_people(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "person_id": pid,
                    "name": data["name"],
                    "enrolled_at": data.get("enrolled_at", ""),
                    "embedding_count": len(data["embeddings"]),
                }
                for pid, data in self.known_faces.items()
            ]

    def db_size(self) -> int:
        with self._lock:
            return len(self.known_faces)

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save_database(self) -> None:
        with self._lock:
            data = {
                pid: {
                    "name": d["name"],
                    "enrolled_at": d.get("enrolled_at", ""),
                    "embeddings": [e.tolist() for e in d["embeddings"]],
                }
                for pid, d in self.known_faces.items()
            }
        with open(self.db_path, "w") as f:
            json.dump(data, f)
        print(f"[DB] Saved {len(data)} people → {self.db_path}")

    def _load_default_database(self) -> None:
        """Load a default set of known faces."""
        source_face_dir = "projects/Dataset/images/"
        folder_path = Path(os.path.abspath(source_face_dir))

        images = list(folder_path.rglob("*.jpg"))
        for img_path in images:
            key = str(img_path.parent).split("/")[-1]
            img = cv2.imread(img_path)
            faces = self.app.get(img)
            self.enroll_from_embedding(key, key, faces[0].embedding)

        

    def _load_database(self) -> None:
        if not self.db_path.exists():
            # self._load_default_database()
            # print("[DB] Loaded default database.")
            print(f"[DB] No database at {self.db_path}, starting empty.")
            return
            
        with open(self.db_path) as f:
            raw: dict = json.load(f)

        migrated: dict = {}
        for key, val in raw.items():
            if isinstance(val, list):
                # ── Migrate old format: {name: [emb, ...]} ──
                migrated[key] = {
                    "name": key,
                    "enrolled_at": "",
                    "embeddings": [np.array(e) for e in val],
                }
            else:
                migrated[key] = {
                    "name": val["name"],
                    "enrolled_at": val.get("enrolled_at", ""),
                    "embeddings": [np.array(e) for e in val["embeddings"]],
                }
        self.known_faces = migrated
        print(f"[DB] Loaded {len(self.known_faces)} people.")

    def _save_sessions(self) -> None:
        with open(self.sessions_path, "w") as f:
            json.dump(self._sessions, f)

    def _load_sessions(self) -> None:
        if not self.sessions_path.exists():
            return
        with open(self.sessions_path) as f:
            self._sessions = json.load(f)
        print(f"[Sessions] Loaded {len(self._sessions)} sessions.")

    # ── Session management ────────────────────────────────────────────────────

    def start_session(self, session_name: str) -> dict:
        global recording_active
        with self._lock:
            session_id = str(uuid.uuid4())
            self._session = {
                "session_id": session_id,
                "session_name": session_name,
                "started_at": datetime.now(timezone.utc).isoformat("#", "seconds"),
                "ended_at": None,
                "duration_seconds": None,
                "present_count": 0,
                "records": {},  # {person_id: {name, first_seen, last_seen, seen_count}}
                "video_file": None,
            }
        return {"success": True}

    def stop_session(self) -> dict:
        with self._lock:
            if not self._session:
                return {"success": False, "error": "No active session"}
            session = dict(self._session)
            ended_at = datetime.now(timezone.utc)
            started_at = datetime.fromisoformat(session["started_at"])
            session["ended_at"] = ended_at.isoformat("#", "seconds")
            session["duration_seconds"] = int((ended_at - started_at).total_seconds())
            session["present_count"] = len(session["records"])
            self._sessions.append(session)
            self._session = None
                
        self._save_sessions()
        return {"success": True, "summary": {"present_count": session["present_count"]}}

    def record_sighting(self, person_id: str, name: str) -> None:
        """Call each time a known person is seen in the current session."""
        with self._lock:
            if not self._session:
                return
            now = datetime.now(timezone.utc).isoformat()
            rec = self._session["records"]
            if person_id not in rec:
                rec[person_id] = {
                    "name": name,
                    "first_seen": datetime.now(timezone.utc).replace(tzinfo=None).isoformat("#", "seconds"),
                    "last_seen": datetime.now(timezone.utc).replace(tzinfo=None).isoformat("#", "seconds"),
                    "seen_count": 1,
                }
            else:
                rec[person_id]["last_seen"] = datetime.now(timezone.utc).replace(tzinfo=None).isoformat("#", "seconds")
                rec[person_id]["seen_count"] += 1

            print(rec)
            self._session["present_count"] = len(rec)

    def session_present_count(self) -> int:
        with self._lock:
            return len(self._session["records"]) if self._session else 0

    def session_active(self) -> bool:
        with self._lock:
            return self._session is not None

    def is_first_seen_this_session(self, person_id: str) -> bool:
        """True only on the first sighting of person_id in the current session."""
        with self._lock:
            if not self._session:
                return False
            rec = self._session["records"].get(person_id)
            return rec is not None and rec.get("seen_count", 0) == 1

    # ── Session queries ───────────────────────────────────────────────────────

    def list_sessions(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "session_id": s["session_id"],
                    "session_name": s["session_name"],
                    "started_at": s["started_at"],
                    "ended_at": s.get("ended_at"),
                    "present_count": s.get("present_count", len(s.get("records", {}))),
                    "duration_seconds": s.get("duration_seconds", 0),
                }
                for s in reversed(self._sessions)
            ]

    def get_session(self, session_id: str) -> dict | None:
        with self._lock:
            for s in self._sessions:
                if s["session_id"] == session_id:
                    return s
            return None

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            before = len(self._sessions)
            self._sessions = [s for s in self._sessions if s["session_id"] != session_id]
            changed = len(self._sessions) < before
        if changed:
            self._save_sessions()
        return changed

    def delete_all_sessions(self) -> bool:
        with self._lock:
            self._sessions.clear()
        self._save_sessions()
        return True

    # ── Folder / batch enroll ─────────────────────────────────────────────────

    def preview_folder(self, folder: str) -> dict:
        folder_path = Path(folder)
        if not folder_path.is_dir():
            return {"success": False, "error": "Folder not found"}
        images = [
            p.name for p in folder_path.rglob("*")
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]
        return {"success": True, "count": len(images), "files": images}

    def _parse_filename(self, stem: str) -> tuple[str, str]:
        """
        Parse 'FirstName_LastName_ID' → (name, person_id).
        Supports any number of name parts; last segment is person_id.
        E.g. 'Alice_Smith_ST001' → ('Alice Smith', 'ST001')
             'Bob_ST002'         → ('Bob', 'ST002')
             'Carol'             → ('Carol', 'carol')
        """
        parts = stem.split("_")
        if len(parts) >= 2:
            person_id = parts[-1]
            name = " ".join(parts[:-1])
        else:
            name = parts[0]
            person_id = parts[0].lower()
        return name, person_id

    def _enroll_from_file(
        self,
        image_path: str,
        person_id: str,
        name: str,
        min_score: float,
    ) -> dict:
        """Enroll a single image. Returns a result dict."""

        img = cv2.imread(image_path)
        if img is None:
            return {"status": "failed", "reason": "cannot read image"}

        faces = self.app.get(img)
        if not faces:
            return {"status": "failed", "reason": "no face detected"}

        face = faces[0]
        det_score = float(face.det_score)
        if det_score < min_score:
            return {
                "status": "failed",
                "reason": f"detection score {det_score:.2f} < threshold {min_score}",
                "detection_score": round(det_score, 3),
            }

        self.enroll_from_embedding(person_id, name, face.embedding)
        return {"status": "enrolled", "detection_score": round(det_score, 3)}

    def folder_enroll(
        self,
        folder: str,
        overwrite: bool = False,
        min_score: float = 0.5,
    ) -> dict:
        folder_path = Path(folder)
        if not folder_path.is_dir():
            return {"success": False, "error": "Folder not found"}

        images = [
            p for p in folder_path.rglob("*")
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]

        results, enrolled, skipped, failed = [], 0, 0, 0

        for img_path in images:
            name, _ = self._parse_filename(img_path.stem)

            person_id = str(img_path).split("/")[-2]
            result = self._enroll_from_file(
                str(img_path), person_id, person_id, min_score
            )

            result["file"] = img_path.name
            result["name"] = person_id
            result["person_id"] = person_id
            results.append(result)

            if result["status"] == "enrolled":
                enrolled += 1
            elif result["status"] == "skipped":
                skipped += 1
            else:
                failed += 1

        return {
            "success": True,
            "total": len(images),
            "enrolled": enrolled,
            "skipped": skipped,
            "failed": failed,
            "results": results,
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
face_analyzer = FaceAnalyzer(model_name="buffalo_m", ctx_id=0, det_size=(256, 256))


# ═════════════════════════════════════════════════════════════════════════════
# Video pipeline
# ═════════════════════════════════════════════════════════════════════════════

def video_stream_thread(
    camera_id: int = 2,
    frame_width: int = 640,
    frame_height: int = 480,
    fps: int = 30,
) -> None:
    """Capture frames from the camera and push them onto frame_queue."""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"[Camera] Cannot open camera {camera_id}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    print(
        f"[Camera] Opened — "
        f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}×"
        f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ {fps} fps"
    )

    retry_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                retry_count += 1
                if retry_count >= 5:
                    print("retry_count",retry_count)
                    print("[Camera] Failed to read frame")
                    break
                time.sleep(0.1)
                continue
            else:
                retry_count = 0
            try:
                frame_queue.put_nowait(frame.copy())
            except queue.Full:
                pass  # drop frame; keep latency low
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        print("[Camera] Released")


def _encode_crop(img: np.ndarray, bbox) -> str:
    """Return a base64-encoded JPEG of the face bounding box."""
    h, w = img.shape[:2]
    x1, y1, x2, y2 = map(int, bbox)
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        return ""
    _, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buf).decode()


def face_analyze_thread() -> None:
    """
    Consume frames from frame_queue, run detection + recognition,
    update current_faces and output_frame, and capture frames for video recording.
    """
    global output_frame, current_faces, recording_active

    while True:
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        raw_faces = face_analyzer.app.get(frame)
        annotated = frame.copy()
        new_faces: list[dict] = []

        for face in raw_faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            person_id, name, score = face_analyzer.recognize(face.embedding)
            identified = person_id != "unknown"

            first_seen = False
            if identified:
                face_analyzer.record_sighting(person_id, name)
                first_seen = face_analyzer.is_first_seen_this_session(person_id)

            crop_b64 = _encode_crop(frame, face.bbox)

            # Annotate the frame
            color = (0, 255, 0) if identified else (0, 0, 255)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            # label = f"{name} ({score:.2f})" if identified else f"Unknown ({score:.2f})"
            label = f"{name}" if identified else f"Unknown"
            cv2.putText(
                annotated, label, (x1, max(0, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2,
            )

            new_faces.append({
                "identified": identified,
                "person_id": person_id,
                "matches": [{"name": name, "similarity": round(score, 4)}] if identified else [],
                "detection_score": float(face.det_score),
                "first_seen_this_session": first_seen,
                "last_seen": None,
                # Internal fields — not sent to frontend directly
                "embedding": face.embedding,
                "crop_b64": crop_b64,
            })

        with current_faces_lock:
            current_faces = new_faces

        with frame_lock:
            output_frame = annotated


def generate_frames():
    """MJPEG generator for /video_feed."""
    while True:
        with frame_lock:
            if output_frame is None:
                time.sleep(0.02)
                continue
            _, buffer = cv2.imencode(
                ".jpg", output_frame, [cv2.IMWRITE_JPEG_QUALITY, 70]
            )
            frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n"
            + frame_bytes + b"\r\n"
        )
        time.sleep(0.02)