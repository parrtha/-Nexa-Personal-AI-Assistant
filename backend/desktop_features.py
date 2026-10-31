
import platform
import psutil
import os

from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Query
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
import json
import uuid
from threading import Lock
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel
router = APIRouter(prefix="/api", tags=["Desktop Tools"])

# ==================================================
# REMINDERS
# ==================================================

REMINDER_FILE = Path(__file__).parent / "reminders.json"
reminder_lock = Lock()


class ReminderCreate(BaseModel):
    title: str
    description: str = ""
    remind_at: str


def load_reminders():
    with reminder_lock:
        if not REMINDER_FILE.exists():
            return []

        try:
            with open(REMINDER_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data if isinstance(data, list) else []

        except (json.JSONDecodeError, OSError):
            return []


def save_reminders(reminders):
    with reminder_lock:
        temporary_file = REMINDER_FILE.with_suffix(".tmp")

        with open(temporary_file, "w", encoding="utf-8") as file:
            json.dump(reminders, file, indent=4, ensure_ascii=False)

        temporary_file.replace(REMINDER_FILE)


@router.get("/reminders")
def get_reminders():
    return {
        "success": True,
        "reminders": load_reminders()
    }


@router.post("/reminders")
def create_reminder(request: ReminderCreate):
    title = request.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Reminder title cannot be empty."
        )

    if len(title) > 150:
        raise HTTPException(
            status_code=400,
            detail="Reminder title is too long."
        )

    try:
        reminder_time = datetime.fromisoformat(
            request.remind_at
        )

        if reminder_time.tzinfo is not None:
            reminder_time = reminder_time.astimezone().replace(
                tzinfo=None
            )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid reminder date or time."
        )

    reminder = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": request.description.strip(),
        "remind_at": reminder_time.isoformat(timespec="minutes"),
        "completed": False,
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    reminders = load_reminders()
    reminders.append(reminder)
    save_reminders(reminders)

    return {
        "success": True,
        "reminder": reminder
    }


@router.patch("/reminders/{reminder_id}")
def update_reminder(reminder_id: str):
    reminders = load_reminders()

    for reminder in reminders:
        if reminder["id"] == reminder_id:
            reminder["completed"] = not reminder.get(
                "completed", False
            )

            save_reminders(reminders)

            return {
                "success": True,
                "reminder": reminder
            }

    raise HTTPException(
        status_code=404,
        detail="Reminder not found."
    )


@router.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: str):
    reminders = load_reminders()

    updated = [
        reminder for reminder in reminders
        if reminder["id"] != reminder_id
    ]

    if len(updated) == len(reminders):
        raise HTTPException(
            status_code=404,
            detail="Reminder not found."
        )

    save_reminders(updated)

    return {
        "success": True,
        "message": "Reminder deleted."
    }
# ==========================================
# OPEN FILE
# ==========================================

class OpenFileRequest(BaseModel):
    path: str


@router.post("/files/open")
def open_file(request: OpenFileRequest):
    file_path = Path(request.path).resolve()

    # Only allow files inside configured search folders.
    allowed = False

    for root in SEARCH_LOCATIONS:
        try:
            resolved_root = root.resolve()

            if file_path.is_relative_to(resolved_root):
                allowed = True
                break
        except (OSError, ValueError):
            continue

    if not allowed:
        raise HTTPException(
            status_code=403,
            detail="This file location is not allowed."
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    try:
        os.startfile(str(file_path))

        return {
            "success": True,
            "message": "File opened successfully.",
            "name": file_path.name
        }

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not open file: {error}"
        )
# ==================================================
# SYSTEM MONITOR
# ==================================================

@router.get("/system")
def get_system_info():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")

    battery = psutil.sensors_battery()

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram": {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "used_gb": round(memory.used / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent": disk.percent
        },
        "battery": {
            "percent": battery.percent if battery else None,
            "plugged_in": battery.power_plugged if battery else None
        },
        "system": {
            "operating_system": platform.system(),
            "version": platform.version(),
            "processor": platform.processor()
        }
    }


# ==================================================
# FILE SEARCH
# ==================================================

SEARCH_LOCATIONS = [
    Path.home() / "Desktop",
    Path("D:/Downloads"),
    Path.home() / "Documents"
]

EXCLUDED_FOLDERS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "AppData"
}

MAX_RESULTS = 100
MAX_SCANNED_FILES = 20000


@router.get("/files/search")
def search_files(q: str = Query(..., min_length=1, max_length=150)):
    query = q.strip()

    if not query:
        return {
            "query": query,
            "count": 0,
            "results": []
        }

    results = []
    scanned = 0

    for root in SEARCH_LOCATIONS:

        if not root.exists():
            continue

        for current_path, directories, filenames in os.walk(
            root,
            onerror=lambda error: None
        ):

            directories[:] = [
                folder for folder in directories
                if folder not in EXCLUDED_FOLDERS
            ]

            for filename in filenames:

                scanned += 1

                if scanned > MAX_SCANNED_FILES:
                    break

                if query.casefold() not in filename.casefold():
                    continue

                file_path = Path(current_path) / filename

                try:
                    stat = file_path.stat()

                    results.append({
                        "name": filename,
                        "path": str(file_path),
                        "size_bytes": stat.st_size,
                        "modified": datetime.fromtimestamp(
                            stat.st_mtime
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "location": root.name
                    })

                except (PermissionError, OSError):
                    continue

                if len(results) >= MAX_RESULTS:
                    break

            if scanned > MAX_SCANNED_FILES:
                break

            if len(results) >= MAX_RESULTS:
                break

        if scanned > MAX_SCANNED_FILES:
            break

        if len(results) >= MAX_RESULTS:
            break

    return {
        "query": query,
        "count": len(results),
        "results": results,
        "scan_limit_reached": scanned > MAX_SCANNED_FILES
    }
