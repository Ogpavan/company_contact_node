import os
import sys

from flask import Flask, jsonify, request

# Ensure repo root is importable in serverless runtime.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fetch_company_phone import build_url, extract_phones, run_curl

app = Flask(__name__)


@app.get("/")
def phone_lookup():
    company = request.args.get("q") or request.args.get("company")
    if not company:
        return jsonify({"error": "Missing required query param: q (or company)"}), 400

    try:
        url = build_url(company)
        response_text = run_curl(url)
        phones = extract_phones(response_text)
        return jsonify(
            {
                "company": company,
                "phones": phones,
                "count": len(phones),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
