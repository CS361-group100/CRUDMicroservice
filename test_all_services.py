#===============================================================================
# File:        test_all_services.py
# Version:     0.0.1
# Project:     Group Project - Assignment 7
# Authors:     Skyler Smith
#              Crystal Wolf
#              Aaron Nelson
#              Tesneem El-kheir
#              Rachel Luginbill
#
# Created:     Winter 2026 | CS163-400
# Description:
#   A Python program for testing all the Group 100 microservices.
#===============================================================================

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

#-------------------------------------------------------------------------------

def test_login_ms(base_url: str = "http://localhost:5000") -> None:
    """
    """
    print("=== Testing Login MS ===")

    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "StrongPassword123"  # >= 10 chars (their requirement)

    def post_json(path: str, payload: dict) -> None:
        url = base_url.rstrip("/") + path
        body = json.dumps(payload).encode("utf-8")
        req = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        print(f"> POST {url}")
        print(json.dumps(payload, indent=2))

        try:
            with urlopen(req, timeout=5) as resp:
                resp_body = resp.read().decode("utf-8", errors="replace")
                print(f"< Status: {resp.status}")
                if resp_body.strip():
                    try:
                        print(json.dumps(json.loads(resp_body), indent=2))
                    except json.JSONDecodeError:
                        print(resp_body)
                print()
                return

        except HTTPError as e:
            resp_body = e.read().decode("utf-8", errors="replace")
            print(f"< Status: {e.code}")
            if resp_body.strip():
                try:
                    print(json.dumps(json.loads(resp_body), indent=2))
                except json.JSONDecodeError:
                    print(resp_body)
            print()
            return

        except URLError as e:
            print(f"ERROR: Could not reach login service: {e}")
            return

    # Register
    post_json("/auth/register", {"username": username, "password": password})

    # Login
    post_json("/auth/login", {"username": username, "password": password})

    # Optional quick negative test (bad password -> 401)
    post_json("/auth/login", {"username": username, "password": "WrongPassword123"})


#-------------------------------------------------------------------------------

def test_crud_ms(crud_repo_root: Path) -> None:
    """
    """
    print("=== Testing CRUD MS ===")

    requests_dir = crud_repo_root / "requests"
    responses_dir = crud_repo_root / "responses"
    requests_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    #---------------------------------------------------------------------------
    # CREATE
    #---------------------------------------------------------------------------
    request_id_create = str(uuid.uuid4())

    create_req: Dict[str, Any] = {
        "request_id": request_id_create,
        "user_id": "user01",
        "resource_type": "job_application",
        "operation": "create",
        "resource_data": {
            "company": "ACME",
            "position": "Intern",
            "status": "applied"
        }
    }

    create_req_path = requests_dir / f"{request_id_create}.json"
    create_resp_path = responses_dir / f"{request_id_create}_response.json"

    print("> CRUD create request:")
    print(json.dumps(create_req, indent=2))

    with open(create_req_path, "w", encoding="utf-8") as f:
        json.dump(create_req, f, indent=2)
        f.write("\n")

    deadline = time.time() + 10.0
    create_resp: Dict[str, Any] = {}

    while time.time() < deadline:

        if create_resp_path.exists() and create_resp_path.stat().st_size > 0:
            try:
                with open(create_resp_path, "r", encoding="utf-8") as f:
                    create_resp = json.load(f)
                break
            except json.JSONDecodeError:
                pass
        time.sleep(0.1)

    if not create_resp:
        print(f"ERROR: Timed out waiting for CRUD create response: {create_resp_path}")
        return

    print("> CRUD create response:")
    print(json.dumps(create_resp, indent=2))

    resource_id = None
    try:
        resource_id = create_resp.get("data", {}).get("resource_id")
    except Exception:
        resource_id = None

    if not resource_id:
        print("[WARN] No data.resource_id returned; skipping delete test.")
        return

    #---------------------------------------------------------------------------
    # DELETE (optional)
    #---------------------------------------------------------------------------
    request_id_delete = str(uuid.uuid4())

    delete_req: Dict[str, Any] = {
        "request_id": request_id_delete,
        "user_id": "user01",
        "resource_type": "job_application",
        "operation": "delete",
        "resource_id": resource_id
    }

    delete_req_path = requests_dir / f"{request_id_delete}.json"
    delete_resp_path = responses_dir / f"{request_id_delete}_response.json"

    print("> CRUD delete request:")
    print(json.dumps(delete_req, indent=2))

    with open(delete_req_path, "w", encoding="utf-8") as f:
        json.dump(delete_req, f, indent=2)
        f.write("\n")

    deadline = time.time() + 10.0
    delete_resp: Dict[str, Any] = {}

    while time.time() < deadline:
        if delete_resp_path.exists() and delete_resp_path.stat().st_size > 0:
            try:
                with open(delete_resp_path, "r", encoding="utf-8") as f:
                    delete_resp = json.load(f)
                break
            except json.JSONDecodeError:
                pass
        time.sleep(0.1)

    if not delete_resp:
        print(f"ERROR: Timed out waiting for CRUD delete response: {delete_resp_path}")
        return

    print("> CRUD delete response:")
    print(json.dumps(delete_resp, indent=2))


#-------------------------------------------------------------------------------

def test_ims() -> None:
    """
    """
    print("=== Testing IMS ===")

    control_file = Path("image-service") / "control.json"

    if not control_file.exists():
        print("ERROR: control.json not found.")
        return

    request = {
        "command": "ascii",
        "args": {
            "path": "examples/gastly.png"
        }
    }

    # Print the request.
    print("> Sending request:")
    print(json.dumps(request, indent=2))

    # Write request (overwrite file).
    with open(control_file, "w", encoding="utf-8") as f:
        json.dump(request, f, indent=2)
        f.write("\n")

    timeout = time.time() + 10

    # Wait for response / Poll control file until response is received (if any).
    while time.time() < timeout:

        if control_file.exists() and control_file.stat().st_size > 0:
            try:
                with open(control_file, "r", encoding="utf-8") as f:
                    response = json.load(f)

                # Only treat it as response if it has status key.
                if isinstance(response, dict) and "status" in response:
                    print("> Received response:")
                    print(json.dumps(response, indent=2))
                    return
            except json.JSONDecodeError:
                pass

        time.sleep(0.1)

    print("ERROR: Timed out waiting for IMS response.")


#-------------------------------------------------------------------------------

def main() -> int:
    test_ims()
    test_crud_ms(Path("./CRUDMicroservice"))
    test_login_ms()
    return 0


#-------------------------------------------------------------------------------

if __name__ == "__main__":
    raise SystemExit(main())