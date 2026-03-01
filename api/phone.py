from flask import Flask, jsonify, request

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


# Optional local run: python api/phone.py
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
