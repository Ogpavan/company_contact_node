import argparse
import re
import sys
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen

BASE_URL = "https://www.google.com/search?tbm=map&authuser=0&hl=en&gl=in&pb=!4m12!1m3!1d53758.17799235329!2d79.43663169999999!3d28.366764999999997!2m3!1f0!2f0!3f0!3m2!1i870!2i735!4f13.1!7i20!10b1!12m26!1m5!18b1!30b1!31m1!1b1!34e1!2m4!5m1!6e2!20e3!39b1!10b1!12b1!13b1!16b1!17m1!3e1!20m4!5e2!6b1!8b1!14b1!46m1!1b0!96b1!99b1!19m4!2m3!1i360!2i120!4i8!20m65!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m33!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!1m3!1e9!2b1!3e2!2b1!9b0!15m16!1m7!1m2!1m1!1e2!2m2!1i195!2i195!3i20!1m7!1m2!1m1!1e2!2m2!1i195!2i195!3i20!22m6!1siWekaenqNYOX4-EPh5fb-Qc%3A4!2s1i%3A0%2Ct%3A11887%2Cp%3AiWekaenqNYOX4-EPh5fb-Qc%3A4!7e81!12e3!17siWekaenqNYOX4-EPh5fb-Qc%3A49!18e15!24m112!1m30!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m19!3b1!4b1!5b1!6b1!9b1!13b1!14b1!17b1!20b1!21b1!22b1!27m1!1b0!28b0!32b1!33m1!1b1!34b1!36e2!10m1!8e3!11m1!3e1!14m1!3b0!17b1!20m2!1e3!1e6!24b1!25b1!26b1!27b1!29b1!30m1!2b1!36b1!37b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!61m2!1m1!1e1!65m5!3m4!1m3!1m2!1i224!2i298!72m22!1m8!2b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3sother_user_google_review_posts__and__hotel_and_vr_partner_review_posts!6m1!1e1!9b1!89b1!90m2!1m1!1e2!98m3!1b1!2b1!3b1!103b1!113b1!114m3!1b1!2m1!1b1!117b1!122m1!1b1!126b1!127b1!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i530!2i735!1m6!1m2!1i820!2i0!2m2!1i870!2i735!1m6!1m2!1i0!2i0!2m2!1i870!2i20!1m6!1m2!1i0!2i715!2m2!1i870!2i735!34m19!2b1!3b1!4b1!6b1!8m6!1b1!3b1!4b1!5b1!6b1!7b1!9b1!12b1!14b1!20b1!23b1!25b1!26b1!31b1!37m1!1e81!42b1!47m0!49m10!3b1!6m2!1b1!2b1!7m2!1e3!2b1!8b1!9b1!10e2!50m4!2e2!3m2!1b1!3b1!67m5!7b1!10b1!14b1!15m1!1b0!69i769!77b1&q=Iraitech%20Innovations%20%26%20Technologies%20Pvt.Ltd&oq=Iraitech%20Innovations%20%26%20Technologies%20Pvt.Ltd&gs_l=maps.12..38i72k1l5.28180.28180.1.32180.1.1.....264.264.2-1.1.....0....1..maps..0.1.271.0..38i39k1j38.&tch=1&ech=1"

HEADERS = [
    "accept: */*",
    "accept-language: en-US,en;q=0.9,hi;q=0.8",
    "available-dictionary: :z75bhC5Oc+ga2vfm1dqAdEQcX4xIehqrAlrF5DsptWE=:",
    "priority: u=1, i",
    "referer: https://www.google.com/",
    "sec-ch-ua: \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Brave\";v=\"144\"",
    "sec-ch-ua-mobile: ?0",
    "sec-ch-ua-platform: \"Windows\"",
    "sec-fetch-dest: empty",
    "sec-fetch-mode: cors",
    "sec-fetch-site: same-origin",
    "sec-gpc: 1",
    "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "x-maps-diversion-context-bin: CAE=",
]

# Keep cookie in a separate variable to avoid accidental edits.
COOKIE = "__Secure-BUCKET=CMwB; SEARCH_SAMESITE=CgQI2p8B; __Secure-ENID=30.SE=VU7EQ2hZtzyuC0v1cQ9rxHdXbPpYD5sFtwZm8RewodbOqnIMgt58esNQcRAa9tvLdBpRqA1rfikEv8UMQvRUu0c1Ab9FuMDM0h9UFhtkfKisY4VbrBMAhQX0pCXv9cS-HVmZd_pN5DmRvgY1ndQtAUyXqzFkDp12J8zudXZbWXjvMr_AUvy1BJ75aimxo6z5OClODEGCnpIzBy_HRm-2IEyTcqJFDI9j0TVPMjHVVBB2zb87FD9KA9XTAR99ZtfspSdl8oLHAxut4Q359vLr1v1ty3773RxpvEmDa7CIRwSQWHrVsE1eAaXjh1vboI1mw08eWxNZRFIvBslvi-VgIg3QKzee2cROZer_LRLfUhwFcaGVGjxEAgV8A65bXYpWEDA; OTZ=8490627_34_34__34_; AEC=AaJma5sqCWIn24bn_41x5CWWHkrcGDzlm050ck7fmTmrBUkwfGZikqLtgJE; SID=g.a0007QgXrwNyXddkGqzpgzuHJ-WQVS8xuaZXXopcgMnUIK2Ml7pAIYJaGvuk9phpWMtwLciFuQACgYKAX0SARcSFQHGX2MiRRvQn16KnlsuzPJBVLqOAxoVAUF8yKr6d0M_H-5pZTnrubI81XDC0076; __Secure-1PSID=g.a0007QgXrwNyXddkGqzpgzuHJ-WQVS8xuaZXXopcgMnUIK2Ml7pAD5AQ9tpDMlwchFOaA6OOQgACgYKASASARcSFQHGX2MizI-m2l2namRElsotfg4G4BoVAUF8yKqkA4q64xJJdiOzeiFwazcF0076; __Secure-3PSID=g.a0007QgXrwNyXddkGqzpgzuHJ-WQVS8xuaZXXopcgMnUIK2Ml7pA8071q3KmbrwW_qglxS4DiAACgYKAcASARcSFQHGX2Mis4aOgXqGp2k35s9oV-XD5xoVAUF8yKrxPCIaxsJHvP3UDBfMspVe0076; HSID=AQ9oWHYShxzBkxIYZ; SSID=Azp6YKRZeTR_tziha; APISID=2LmSER6k185cKwIF/AGgov3VtwZ1lcygtf; SAPISID=WLP1ttoszu3uYv6W/A8uUQUwAnuYQ1u3SD; __Secure-1PAPISID=WLP1ttoszu3uYv6W/A8uUQUwAnuYQ1u3SD; __Secure-3PAPISID=WLP1ttoszu3uYv6W/A8uUQUwAnuYQ1u3SD; __Secure-1PSIDTS=sidts-CjYBBj1CYhw1xEsipI7TCnK6wwM4bwaLWEwvfJl2I-XC7dOdT1351uE9d_IExNhUNTaVYYQnZEMQAA; __Secure-1PSIDRTS=sidts-CjYBBj1CYhw1xEsipI7TCnK6wwM4bwaLWEwvfJl2I-XC7dOdT1351uE9d_IExNhUNTaVYYQnZEMQAA; __Secure-3PSIDTS=sidts-CjYBBj1CYhw1xEsipI7TCnK6wwM4bwaLWEwvfJl2I-XC7dOdT1351uE9d_IExNhUNTaVYYQnZEMQAA; __Secure-3PSIDRTS=sidts-CjYBBj1CYhw1xEsipI7TCnK6wwM4bwaLWEwvfJl2I-XC7dOdT1351uE9d_IExNhUNTaVYYQnZEMQAA; NID=529=UB6U1ST2YeMXRkIGYrWH-krJl8BIprZ_Rg1u5uFoKvnp15JJC1wU2T4EublpG881zaDUGOcH9IiOSN5bVL-lUojU5DG7rCBZKhPO94WtpdmXpyjmMgZQPbWIKRQW73mgftaVT3oy3VuMK_-2alVRx2PtHKtXl5EkSKVlPj37HaX28XlDPt3q6B5G_h9F_6Fj6N2Tax5eNP67-c1Fe9KsSVz0EYgynUY5VF8JyOnCDCWhVpKUezwyHjc16cM-5kysipRiA1W3MLLjhqlySXLJA3Sez4FK5v6j9OX8GXZWyZ3KLZMKDC7e6_woD4G2xHXneOxtcMNt16nyhhFivZIFnBYpPOEosCdbTTBsWwB9znhT6nHC6_YDJLFHF2vIpoOx5Dpk0VPHgTTnwS_2VLor8TdH71dYD88lR6IKBWp0sMjXfHABp2oXsmVBQ4MDSpzT5gevv70bdCo1L0qAv5-1SS5nbYoj8cM6TembH7Aiu-jkBiiBJClEze-Bez7dI4Lja75WLXglKQxA10h7G3v0eUxOQMDbz-dfEeIIbo7KuR26WYOmT1b8KRtlOgrNKm5yXGkr3BCm-PpQK79UA-2bVYTAo7qOaC6dSOA2AHgOl3Gp6uhWZ1LWCaMtDuLYU5G0rXkYonfeA9GhU7uUPgGjGsSnnPVmCIx3f9rpOVmYFXHG-fQB1bANK-SWIfxxKrITpPDJws5kw7PLF0vyZ3r_0TPG8NcZQXj7j_kfIMfv4oPOQZ1DydJzhA-0HCB3TDBGEc8E73UtmPcT7-SzxRHcJRkyVognhfsBSmPxJH-Ov9afHJXvbeaP-cYWQdjKw4D6-RL3qxvstiNFqumLqfd773zXCmxcl_LCeu8t6-YEhNw1t3wRDb0RYpinlFSm2c_VCSC74SvmT9ufgzdDfSlgaGUWNKzuMyRSBZ_z_xTtPUi1_DYrSpkiX-lRT__VXamJ-tnsENMRXDSMJ8tFrlkBKcQJknw1vVGd3_uNvflwbtllCeTTPXOi5CdyStrlRebYebBibrEt-TdiQGFDdZSiX88OhFXbqLJnyg593Ef950t6IO_4rZ_JOzPhgbLhhEXLkSuLnNxEZola8Zl10Zm7sBOa_WIuZmUqK3wcEwYxfKwR2B_o4SvpHwHPsfhyb145DKpo3X7KGHE5EpQbO_WU4mgFqcm8ifuoxg2rCYEzAPSNoZVeLUWDoQRoFHaMnVUtLi3NofphcHZkgJTtGtF41F_b5T2uyVRPOwMjuTm9SecxeHO6_HNognrW1M7EL6DFLVDEKQRdcgT6okoo7yQ980Q5i2atlGJa6OsUhm0ej1v13A9hczJXSR8IBxuFXsd9fqL0hTw2pkA_VI3AsyFpM8gManMs4Tnw7QS__yXO7b8QpsD08HwNMidqUMFgOVDvSG2ofhauqP9yOGp70tokqGK2uOdFol_Vyg83a-t71aGDIV4MZn1Df5cHupNAhqO1c-ol5ocI9IjbhG7RMEwnqxFHpoJYqujn-gna811MBCAHAWwO959bc9oAUt4TQl4bkfmwo_6M3TxejX_pJP4BsIA3cdOC7w0P3trYKwDCVBesf4u-KIRra2KsrcX-v2ZT6qnh_x90WBJV5pRlisTQjqFZ3C46aK9uhHGMN2yLciKhG05AlRvY8xEPXBzbL_WB3GDFOfDQElZTtbnSgW4G5IWtlLN2x13De20iBpGbfh1ZCcykaKE7VZjkGX5XqZvayWmQEZ8bGKSsSdTdefYZX-_snwrKACyPE0rnzFOaph0wHYPlNEW1cuFLohlCsfVMAzWnOw_ng4OzOu-DopFvQm3eHI-mvpfdBoZbBqV06fBxOW83gigHJskxmcUk6D2dlgLanxpszUFex2rozG0mFQRNdsCQfuD0gvMf6HoR4ZsAM9CYxweSN_VkXjZzaQqRiZbdzqjjES8q3uYB6Pcwyt4ApuGwX9G1VlQDYFI9m9WbSfuETPMPZn9v4IlrV7VFLicAfFzbOEjJbuR7NrIfUdUcmiQ_Tk2_w-Ev-C5V4k3BFx3ItBW5zvydlAhIqy_2oCf0mu_Fo6q7p_XoUgPuc16zid3C7Obh9tADyg3QWJbMPsUbtzXYpLxzt-7svvamGksmB2Gcopwqkiv3yulWCLFJiR8yFzvKaBGViUTQ9_jOCxnoW4zcPHy9eB9OLiZXtx-l9AOlDQ_z67kkTvHoYo_E-KP-AIXpAQ9RM8FG55vkeyDp6lMIt8gnB4iawlkVGSQZ1Ae4zhXWcSIWh3uf9A; DV=Y0w7kD0EZdFoUOUcLYCoi47bnkajyplvU3dyzytnNAIAAMBLUjyomhJKigAAAOBRX6N8aZALMQAAAJqRZTKYl-jiDAAAgKlqLJ98RPP0AwAAAA; __Secure-STRP=AD6DogtcU0mbts98EWlf7PnfobpjBhh55M8pHp_oKH8qOr1mk0-Fhd2tOj7mycqzLqmWD77OMsPmY9WX0U8dsove5PP1Xgm5EA; SIDCC=AKEyXzUpQHP8kSGjI2S3UWo3b66yp_MP-hrLG13g0P-_edRFQ05_CODQn23et2BSkeasrkrUXQA; __Secure-1PSIDCC=AKEyXzUT1EFldgEJXIAjNwwbEIdXckNnKVcAyr6sB71AyS9IheyWl3z8TBSU9LukghcDbw9w9Ts; __Secure-3PSIDCC=AKEyXzXJu8NAMLX7tG28Y42h5OJRWARwM2fH1WqtzOkem1UU0-tXPYYe2yxquiP88WvVGHvqK1k; SIDCC=AKEyXzWm8V4hXyzhK3Kdp8AHwaeMbPZFi9AXYpaZvT8JgoqMWqYY_iuFOYub4lrwxXufBUXyN-Y; __Secure-1PSIDCC=AKEyXzUdHGrzo-4nx8b8Haz9lVTFfhB5c-Doz_vo4F5CSpkEQpRNyWqqBP9wvYtiv7t2kfhq0QQ; __Secure-3PSIDCC=AKEyXzWOsDkDDKUyx-FFPEjd8IMyQ4PZNj3A4LyGvYev3ejC9qaGpi8Xz-ihcFDQfXqBfQaeiI4"


def build_url(company_name: str) -> str:
    encoded = quote(company_name, safe="")
    url = re.sub(r"([?&]q=)[^&]*", rf"\1{encoded}", BASE_URL, count=1)
    url = re.sub(r"([?&]oq=)[^&]*", rf"\1{encoded}", url, count=1)
    return url


def run_curl(url: str) -> str:
    headers = {}
    for header in HEADERS:
        if ": " in header:
            key, value = header.split(": ", 1)
            headers[key] = value
    headers["Cookie"] = COOKIE

    req = Request(url=url, headers=headers, method="GET")
    with urlopen(req, timeout=30) as resp:
        raw = resp.read() or b""
    return raw.decode("utf-8", errors="replace")


def extract_phones(text: str):
    # Google anti-JSON often escapes separators; decode common forms first.
    variants = [
        text,
        text.replace("\\u003a", ":").replace("\\u0026", "&").replace("\\/", "/"),
        unquote(text),
        unquote(text).replace("\\u003a", ":").replace("\\u0026", "&").replace("\\/", "/"),
    ]

    found = []
    tel_pattern = re.compile(r"tel:\s*(\+?[0-9][0-9\-().\s]{5,}[0-9])", re.IGNORECASE)
    for variant in variants:
        for m in tel_pattern.findall(variant):
            phone = re.sub(r"\s+", " ", m).strip(" .-()")
            digits = re.sub(r"\D", "", phone)
            if 7 <= len(digits) <= 15 and phone not in found:
                found.append(phone)

    return found


def extract_websites(text: str):
    # Pull http/https URLs, then filter common non-website Google endpoints.
    variants = [
        text,
        text.replace("\\u003a", ":").replace("\\u0026", "&").replace("\\/", "/"),
        unquote(text),
        unquote(text).replace("\\u003a", ":").replace("\\u0026", "&").replace("\\/", "/"),
    ]

    urls = []
    seen = set()
    url_pattern = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
    blocked_hosts = (
        "google.com",
        "googleusercontent.com",
        "gstatic.com",
        "googleapis.com",
        "doubleclick.net",
    )

    for variant in variants:
        for raw in url_pattern.findall(variant):
            url = raw.rstrip(").,;]")
            # Clean trailing escape slashes/backslashes from payload artifacts.
            url = url.rstrip("\\/").rstrip("/")
            try:
                host = re.sub(r"^https?://", "", url).split("/", 1)[0].lower()
            except Exception:
                host = ""
            if host and any(host.endswith(b) for b in blocked_hosts):
                continue
            if url not in seen:
                seen.add(url)
                urls.append(url)

    return urls


def main():
    parser = argparse.ArgumentParser(
        description="Search Google Maps payload for a company and extract phone number(s)."
    )
    parser.add_argument("company", help="Company name to search")
    parser.add_argument(
        "--save-raw",
        help="Optional file path to save raw curl response",
        default=None,
    )
    args = parser.parse_args()

    try:
        url = build_url(args.company)
        response_text = run_curl(url)

        if args.save_raw:
            with open(args.save_raw, "w", encoding="utf-8") as f:
                f.write(response_text)

        phones = extract_phones(response_text)
        if not phones:
            print("No phone number found")
            return

        print("Phone numbers found:")
        for p in phones:
            print(p)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
