from flask import Flask, jsonify, request

from fetch_company_phone import build_url, extract_phones, extract_websites, run_curl

app = Flask(__name__)


@app.get("/api")
def api_lookup():
    company = request.args.get("q") or request.args.get("company")
    if not company:
        return jsonify({"error": "Missing required query param: q (or company)"}), 400

    try:
        url = build_url(company)
        response_text = run_curl(url)
        phones = extract_phones(response_text)
        websites = extract_websites(response_text)
        return jsonify(
            {
                "company": company,
                "phones": phones,
                "websites": websites,
                "count": len(phones),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
