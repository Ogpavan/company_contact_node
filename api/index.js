const fs = require("fs");
const path = require("path");

const PY_SOURCE = path.join(process.cwd(), "fetch_company_phone.py");

const HEADERS = [
  "accept: */*",
  "accept-language: en-US,en;q=0.9,hi;q=0.8",
  "available-dictionary: :z75bhC5Oc+ga2vfm1dqAdEQcX4xIehqrAlrF5DsptWE=:",
  "priority: u=1, i",
  "referer: https://www.google.com/",
  'sec-ch-ua: "Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
  "sec-ch-ua-mobile: ?0",
  'sec-ch-ua-platform: "Windows"',
  "sec-fetch-dest: empty",
  "sec-fetch-mode: cors",
  "sec-fetch-site: same-origin",
  "sec-gpc: 1",
  "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
  "x-maps-diversion-context-bin: CAE=",
];

function loadPythonConstants() {
  const source = fs.readFileSync(PY_SOURCE, "utf8");
  const baseMatch = source.match(/^BASE_URL\s*=\s*"([\s\S]*?)"\r?$/m);
  const cookieMatch = source.match(/^COOKIE\s*=\s*"([\s\S]*?)"\r?$/m);

  if (!baseMatch || !cookieMatch) {
    throw new Error("Unable to load BASE_URL/COOKIE from fetch_company_phone.py");
  }

  return {
    baseUrl: baseMatch[1],
    cookie: cookieMatch[1],
  };
}

function buildUrl(baseUrl, companyName) {
  const u = new URL(baseUrl);
  u.searchParams.set("q", companyName);
  u.searchParams.set("oq", companyName);
  return u.toString();
}

function toHeaderObject(cookie) {
  const out = {};
  for (const header of HEADERS) {
    const idx = header.indexOf(": ");
    if (idx > 0) {
      out[header.slice(0, idx)] = header.slice(idx + 2);
    }
  }
  out.Cookie = cookie;
  return out;
}

function safeDecodeURIComponent(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function extractPhones(text) {
  const variants = [
    text,
    text.replace(/\\u003a/g, ":").replace(/\\u0026/g, "&").replace(/\\\//g, "/"),
    safeDecodeURIComponent(text),
    safeDecodeURIComponent(text)
      .replace(/\\u003a/g, ":")
      .replace(/\\u0026/g, "&")
      .replace(/\\\//g, "/"),
  ];

  const found = [];
  const seen = new Set();
  const telPattern = /tel:\s*(\+?[0-9][0-9\-().\s]{5,}[0-9])/gi;

  for (const variant of variants) {
    let match;
    while ((match = telPattern.exec(variant)) !== null) {
      const phone = match[1].replace(/\s+/g, " ").trim().replace(/^[ .()\-]+|[ .()\-]+$/g, "");
      const digits = phone.replace(/\D/g, "");
      if (digits.length >= 7 && digits.length <= 15 && !seen.has(phone)) {
        seen.add(phone);
        found.push(phone);
      }
    }
  }

  return found;
}

function extractWebsites(text) {
  const variants = [
    text,
    text.replace(/\\u003a/g, ":").replace(/\\u0026/g, "&").replace(/\\\//g, "/"),
    safeDecodeURIComponent(text),
    safeDecodeURIComponent(text)
      .replace(/\\u003a/g, ":")
      .replace(/\\u0026/g, "&")
      .replace(/\\\//g, "/"),
  ];

  const found = [];
  const seen = new Set();
  const urlPattern = /https?:\/\/[^\s"'<>]+/gi;
  const blockedHosts = new Set([
    "google.com",
    "googleusercontent.com",
    "gstatic.com",
    "googleapis.com",
    "doubleclick.net",
  ]);

  for (const variant of variants) {
    let match;
    while ((match = urlPattern.exec(variant)) !== null) {
      let url = match[0].replace(/[).,;\]]+$/g, "");
      // Clean trailing escape slashes/backslashes from payload artifacts.
      url = url.replace(/[\\/]+$/g, "");
      let host = "";
      try {
        host = new URL(url).hostname.toLowerCase();
      } catch {
        host = "";
      }
      if (host && [...blockedHosts].some((b) => host === b || host.endsWith(`.${b}`))) {
        continue;
      }
      if (!seen.has(url)) {
        seen.add(url);
        found.push(url);
      }
    }
  }

  return found;
}

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  try {
    const qFromQuery = req.query && (req.query.q || req.query.company);
    const qFromUrl = new URL(req.url, "https://dummy.local").searchParams;
    const company = qFromQuery || qFromUrl.get("q") || qFromUrl.get("company");

    if (!company) {
      return res.status(400).json({ error: "Missing required query param: q (or company)" });
    }

    const { baseUrl, cookie } = loadPythonConstants();
    const url = buildUrl(baseUrl, company);
    const response = await fetch(url, {
      method: "GET",
      redirect: "follow",
      headers: toHeaderObject(cookie),
    });

    const responseText = await response.text();
    if (!response.ok) {
      return res.status(502).json({
        error: `Upstream request failed with status ${response.status}`,
        body_preview: responseText.slice(0, 500),
      });
    }

    const phones = extractPhones(responseText);
    const websites = extractWebsites(responseText);
    return res.status(200).json({
      company,
      phones,
      websites,
      count: phones.length,
    });
  } catch (err) {
    return res.status(500).json({ error: String(err && err.message ? err.message : err) });
  }
};




