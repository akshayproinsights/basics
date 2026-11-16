"""HTTP boundary for the dashboard; no storage or backend imports."""
from datetime import datetime
import math
from time import perf_counter
from urllib.parse import quote

import requests


class ApiError(Exception):
    pass


def status_for(gpa):
    try:
        value = float(gpa)
    except (ValueError, TypeError):
        return "Invalid GPA"
    if not math.isfinite(value) or not 0 <= value <= 10:
        return "Invalid GPA"
    return "Fail" if value <= 3 else "Pass" if value <= 5 else "Excellent"


def normalize(payload, student_id=None):
    if student_id is not None:
        pairs = [(student_id, payload)]
    elif isinstance(payload, dict):
        pairs = list(payload.items())
    elif isinstance(payload, list):
        pairs = [(row.get("id_new"), row) for row in payload if isinstance(row, dict)]
        if len(pairs) != len(payload):
            raise ApiError("The API returned a malformed student list.")
    else:
        raise ApiError("Expected a student dictionary or list from the API.")
    result = []
    for identity, row in pairs:
        if identity is None or not isinstance(row, dict):
            raise ApiError("The API returned a student without a valid ID or record.")
        record = {key: row.get(key) for key in ("full_name", "email", "major", "gpa")}
        record["id_new"] = str(identity)
        record["validate_gpa"] = status_for(record["gpa"])
        record["data_quality"] = "Needs review" if (
            record["validate_gpa"] == "Invalid GPA"
            or any(not isinstance(record[k], str) or not record[k].strip()
                   for k in ("full_name", "email", "major"))
        ) else "Complete"
        result.append(record)
    return result


def id_path(route, student_id):
    return f"/{route}/{quote(str(student_id), safe='')}"


class ApiClient:
    def __init__(self, base_url, activity):
        self.base_url = base_url.strip().rstrip("/")
        self.activity = activity

    def request(self, method, path, **kwargs):
        start, status = perf_counter(), "Network error"
        try:
            response = requests.request(method, self.base_url + path, timeout=10, **kwargs)
            status = response.status_code
            try:
                payload = response.json()
            except ValueError:
                raise ApiError(f"HTTP {status}: API returned a non-JSON response.") from None
            if not response.ok:
                detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
                if isinstance(detail, list):
                    detail = "; ".join(
                        f"{'.'.join(map(str, item.get('loc', [])))}: {item.get('msg', item)}"
                        if isinstance(item, dict) else str(item) for item in detail
                    )
                raise ApiError(f"HTTP {status}: {detail}")
            return payload
        except requests.RequestException as exc:
            raise ApiError(f"Cannot reach the API: {exc}") from exc
        finally:
            self.activity.append({"Time": datetime.now().isoformat(timespec="seconds"),
                                  "Method": method, "Path": path,
                                  "Status": str(status), "Duration (ms)": round((perf_counter() - start) * 1000)})
            del self.activity[:-300]
