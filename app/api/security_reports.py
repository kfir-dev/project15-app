import json
from json import JSONDecodeError
from pathlib import Path

from flask import current_app
from flask_restful import Resource


def load_json_report(filename, report_name):
    reports_directory = Path(current_app.config["SECURITY_REPORTS_DIR"])
    report_path = reports_directory / filename

    try:
        with report_path.open(encoding="utf-8") as report_file:
            return json.load(report_file), None
    except FileNotFoundError:
        return None, ({"message": f"{report_name} report is not available"}, 404)
    except JSONDecodeError:
        return None, ({"message": f"{report_name} report is invalid"}, 500)
    except OSError:
        return None, ({"message": f"Unable to read {report_name} report"}, 500)


class SbomResource(Resource):
    def get(self):
        report, error_response = load_json_report("sbom.json", "SBOM")
        if error_response:
            return error_response

        return report, 200


class ScanReportResource(Resource):
    def get(self):
        report, error_response = load_json_report(
            "scan-report.json",
            "Vulnerability scan",
        )
        if error_response:
            return error_response

        return report, 200
