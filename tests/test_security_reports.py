import json
from pathlib import Path

from flask import current_app


def write_report(filename, report):
    reports_directory = Path(current_app.config["SECURITY_REPORTS_DIR"])
    reports_directory.mkdir(parents=True, exist_ok=True)
    report_path = reports_directory / filename
    report_path.write_text(json.dumps(report), encoding="utf-8")


def test_sbom_returns_404_when_report_is_missing(client):
    response = client.get("/api/security/sbom")

    assert response.status_code == 404
    assert response.get_json()["message"] == "SBOM report is not available"


def test_scan_report_returns_404_when_report_is_missing(client):
    response = client.get("/api/security/scan-report")

    assert response.status_code == 404
    assert response.get_json()["message"] == (
        "Vulnerability scan report is not available"
    )


def test_sbom_returns_latest_json_report(client):
    report = {
        "descriptor": {"name": "syft"},
        "artifacts": [{"name": "Flask", "version": "3.1.3"}],
    }

    with client.application.app_context():
        write_report("sbom.json", report)

    response = client.get("/api/security/sbom")

    assert response.status_code == 200
    assert response.get_json() == report


def test_scan_report_returns_latest_json_report(client):
    report = {
        "scanner": "trivy",
        "summary": {"critical": 0, "high": 2},
    }

    with client.application.app_context():
        write_report("scan-report.json", report)

    response = client.get("/api/security/scan-report")

    assert response.status_code == 200
    assert response.get_json() == report


def test_sbom_rejects_invalid_json(client):
    with client.application.app_context():
        reports_directory = Path(current_app.config["SECURITY_REPORTS_DIR"])
        reports_directory.mkdir(parents=True, exist_ok=True)
        (reports_directory / "sbom.json").write_text(
            "not-json",
            encoding="utf-8",
        )

    response = client.get("/api/security/sbom")

    assert response.status_code == 500
    assert response.get_json()["message"] == "SBOM report is invalid"
