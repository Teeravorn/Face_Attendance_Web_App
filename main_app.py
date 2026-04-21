import csv
import io
import threading
import time
import base64
import json
import asyncio

import cv2
import uvicorn
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from html_template.new_template import HTML_TEMPLATE
import face_analyzer as fa  # import the module so we always see the current globals

app = FastAPI(title="Face Recognition")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list = []
        self.lock = threading.Lock()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        with self.lock:
            self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        with self.lock:
            connections_copy = list(self.active_connections)
        
        disconnected = []
        for connection in connections_copy:
            try:
                await connection.send_json(message)
            except Exception as e:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()
last_frame_send_time = time.time()
frame_send_interval = 0.05  # ~20 fps for WebSocket streaming


# ═════════════════════════════════════════════════════════════════════════════
# UI & WebSocket streaming
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time video and face data streaming."""
    await manager.connect(websocket)
    last_faces_update = time.time()
    
    try:
        while True:
            # Receive any incoming messages (for future extensibility)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Process incoming commands if needed
                print(f"[WS] Received: {data}")
            except asyncio.TimeoutError:
                pass
            
            current_time = time.time()
            
            # Send video frame at controlled interval
            global last_frame_send_time
            if current_time - last_frame_send_time >= frame_send_interval:
                last_frame_send_time = current_time
                
                with fa.frame_lock:
                    if fa.output_frame is not None:
                        _, buffer = cv2.imencode(
                            '.jpg', fa.output_frame,
                            [cv2.IMWRITE_JPEG_QUALITY, 75]
                        )
                        frame_bytes = base64.b64encode(buffer).decode('utf-8')
                        await websocket.send_json({
                            'type': 'frame',
                            'frame': frame_bytes,
                            'timestamp': current_time,
                        })
            
            # Send face data at lower frequency (every 300ms)
            if current_time - last_faces_update >= 0.3:
                last_faces_update = current_time
                
                with fa.current_faces_lock:
                    snapshot = list(fa.current_faces)
                
                faces_out = [
                    {
                        'identified': f['identified'],
                        'matches': f['matches'],
                        'detection_score': f['detection_score'],
                        'first_seen_this_session': f['first_seen_this_session'],
                        'last_seen': f.get('last_seen'),
                    }
                    for f in snapshot
                ]
                
                await websocket.send_json({
                    'type': 'faces',
                    'faces': faces_out,
                    'db_size': fa.face_analyzer.db_size(),
                    'session_present': fa.face_analyzer.session_present_count(),
                    'threshold': fa.face_analyzer.THRESHOLD,
                    'session_active': fa.face_analyzer.session_active(),
                    'timestamp': current_time,
                })
            
            await asyncio.sleep(0.01)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WS] Client disconnected")


@app.get("/video_feed")
async def video_feed():
    """Legacy MJPEG endpoint - kept for backward compatibility."""
    return StreamingResponse(
        fa.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# ═════════════════════════════════════════════════════════════════════════════
# Live face data
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/get_faces")
async def get_faces():
    """
    Returns the current detected faces plus global stats.
    Called every second by the JS polling loop.
    """
    with fa.current_faces_lock:
        snapshot = list(fa.current_faces)

    faces_out = [
        {
            "identified": f["identified"],
            "matches": f["matches"],
            "detection_score": f["detection_score"],
            "first_seen_this_session": f["first_seen_this_session"],
            "last_seen": f.get("last_seen"),
        }
        for f in snapshot
    ]

    return JSONResponse({
        "faces": faces_out,
        "db_size": fa.face_analyzer.db_size(),
        "session_present": fa.face_analyzer.session_present_count(),
        "threshold": fa.face_analyzer.THRESHOLD,
        "session_active": fa.face_analyzer.session_active(),
    })


@app.get("/get_face_crop")
async def get_face_crop(index: int = Query(0, ge=0)):
    """Return the base64-encoded JPEG crop for face at *index* in the last frame."""
    with fa.current_faces_lock:
        if index >= len(fa.current_faces):
            return JSONResponse({"crop_b64": None})
        crop_b64 = fa.current_faces[index].get("crop_b64", "")
    return JSONResponse({"crop_b64": crop_b64})


# ═════════════════════════════════════════════════════════════════════════════
# Enrollment
# ═════════════════════════════════════════════════════════════════════════════

class EnrollRequest(BaseModel):
    face_index: int
    person_id: str
    name: str


@app.post("/enroll")
async def enroll(req: EnrollRequest):
    with fa.current_faces_lock:
        if req.face_index < 0 or req.face_index >= len(fa.current_faces):
            return JSONResponse({"success": False, "error": "Invalid face index"})
        embedding = fa.current_faces[req.face_index]["embedding"]

    ok = fa.face_analyzer.enroll_from_embedding(req.person_id, req.name, embedding)
    return JSONResponse({"success": ok, "name": req.name})


# ═════════════════════════════════════════════════════════════════════════════
# Session management
# ═════════════════════════════════════════════════════════════════════════════

class SessionStartRequest(BaseModel):
    session_name: str


@app.post("/session_start")
async def session_start(req: SessionStartRequest):
    return JSONResponse(fa.face_analyzer.start_session(req.session_name))


@app.post("/session_stop")
async def session_stop():
    return JSONResponse(fa.face_analyzer.stop_session())


# ═════════════════════════════════════════════════════════════════════════════
# Attendance
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/list_sessions")
async def list_sessions():
    return JSONResponse({"sessions": fa.face_analyzer.list_sessions()})


@app.get("/get_session")
async def get_session(session_id: str = Query(...)):
    session = fa.face_analyzer.get_session(session_id)
    if not session:
        return JSONResponse({"session": None, "db_size": 0, "absent_people": []})

    people = {p["person_id"]: p for p in fa.face_analyzer.list_people()}
    present_ids = set(session.get("records", {}).keys())
    absent_people = [
        {"person_id": pid, "name": p["name"]}
        for pid, p in people.items()
        if pid not in present_ids
    ]

    return JSONResponse({
        "session": session,
        "db_size": len(people),
        "absent_people": absent_people,
    })


@app.get("/export_csv")
async def export_csv(session_id: str = Query(...)):
    session = fa.face_analyzer.get_session(session_id)
    if not session:
        return JSONResponse({"error": "Session not found"}, status_code=404)

    people = {p["person_id"]: p for p in fa.face_analyzer.list_people()}
    present_ids = set(session.get("records", {}).keys())

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Person ID", "First Seen", "Last Seen", "Times Seen", "Status"])

    for pid, rec in session.get("records", {}).items():
        writer.writerow([
            rec["name"], pid,
            rec.get("first_seen", ""), rec.get("last_seen", ""),
            rec.get("seen_count", 0), "Present",
        ])

    for pid, p in people.items():
        if pid not in present_ids:
            writer.writerow([p["name"], pid, "", "", 0, "Absent"])

    sess_name = session["session_name"].replace(" ", "_").replace("/", "-").replace(",", "")
    filename = f"{sess_name}_{session_id[:8]}.csv"

    print("export csv filename", filename)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class DeleteSessionRequest(BaseModel):
    session_id: str


@app.post("/delete_session")
async def delete_session(req: DeleteSessionRequest):
    ok = fa.face_analyzer.delete_session(req.session_id)
    return JSONResponse({"success": ok})


@app.post("/delete_all_sessions")
async def delete_all_sessions():
    ok = fa.face_analyzer.delete_all_sessions()
    return JSONResponse({"success": ok})


# ═════════════════════════════════════════════════════════════════════════════
# Face database management
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/list_people")
async def list_people():
    return JSONResponse({"people": fa.face_analyzer.list_people()})


class RenamePersonRequest(BaseModel):
    person_id: str
    name: str


@app.post("/rename_person")
async def rename_person(req: RenamePersonRequest):
    ok = fa.face_analyzer.rename_person(req.person_id, req.name)
    return JSONResponse({"success": ok})


class DeletePersonRequest(BaseModel):
    person_id: str


@app.post("/delete_person")
async def delete_person(req: DeletePersonRequest):
    ok = fa.face_analyzer.delete_person(req.person_id)
    return JSONResponse({"success": ok})


@app.post("/clear_database")
async def clear_database():
    ok = fa.face_analyzer.clear_database()
    return JSONResponse({"success": ok})


# ═════════════════════════════════════════════════════════════════════════════
# Folder / batch enroll
# ═════════════════════════════════════════════════════════════════════════════

class FolderPreviewRequest(BaseModel):
    folder: str


@app.post("/preview_folder")
async def preview_folder(req: FolderPreviewRequest):
    return JSONResponse(fa.face_analyzer.preview_folder(req.folder))


class FolderEnrollRequest(BaseModel):
    folder: str
    overwrite: bool = False
    min_score: float = 0.5


@app.post("/folder_enroll")
async def folder_enroll(req: FolderEnrollRequest):
    return JSONResponse(
        fa.face_analyzer.folder_enroll(req.folder, req.overwrite, req.min_score)
    )


# ═════════════════════════════════════════════════════════════════════════════
# Entry point
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    stream_thread = threading.Thread(target=fa.video_stream_thread, daemon=True)
    process_thread = threading.Thread(target=fa.face_analyze_thread, daemon=True)
    stream_thread.start()
    process_thread.start()
    print("Threads started.")
    print("Open http://localhost:5000 in your browser.")
    uvicorn.run(app, host="0.0.0.0", port=5001)