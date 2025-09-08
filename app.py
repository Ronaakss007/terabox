from flask import Flask, request, jsonify
import requests
import logging
import re
from urllib.parse import urlparse, parse_qs

# --- Flask App ---
app = Flask(__name__)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Global Headers (no cookies here) ---
BASE_HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    'Accept': "application/json, text/plain, */*",
    'Accept-Encoding': "identity",
    'X-Requested-With': "XMLHttpRequest",
    'Content-Type': "application/x-www-form-urlencoded",
    'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
}

# ------------------------------
# Premium Cookies
# ------------------------------
PREMIUM_COOKIES = {
    "ACCOUNT_CHOOSER": "AFx_qI5jWZXx28jIOPcT_ElaPSEZHiA3QVBlE-lkByZzewQ4Mhibrq6ceJjPhODR_LezJHsGL40832prtO7X1NhxFKHOSBGLlaWjCgAFT-X1Vo6eMuefkWdDATDzanzyMaspyhF7zs9w-Bc65Rsk7bAC1H2Ah66oD_ZEA3p0u7JoEPfR6fi3CcpmDm4tiy3n_E-VZVtVhMwQBTJvJsXlmIGSfUReySVwJRVOcm4_RXz88s80aYuMJ4Ro9NhuRrfPqFZKFk0BQdJDRfpuujKIe5W_kjSXlWKMZ6eqGMrILvKCyGVzKS0VXcTI8Zn6KYIOjJ7LkvviLAE5m6Av83gXX_ohu3DDEYXsvhlTPZz6wmAhYoI6gLkF7vwxyktnDMgwTluk14NewbOOW0-_Rco0Jca3It1EYKYRjfmDopY-vZlj9O-dsuT0UHs",
    "AEC": "AVh_V2g6_xNYYkECwncJ9EJFNnbRfYvCd2tRCeocw5uVyNNabv_BZq8GTQ",
    "APISID": "toSWgLyAkhHol31J/Aq9swLTjSh8izrHE6",
    "browserid": "6vvQN6l3QzBm74qM_T0faF8vUFn89d-g6yi86LJZ6ENW6zc7v77UWllhVtw=",
    "csrfToken": "U4-YrtqNaI3-DT6QKkIn8-HS",
    "HSID": "AG2K7YhqoYkoNsbC2",
    "lang": "en",
    "LSID": "s.IN|s.youtube:g.a0001AhgbxhhlnVGvDG6I3weSULiTHhLznBxudPW7AHmldFxpZBzTKH2adXLDGH6_M4QWP7-zgACgYKAf4SARcSFQHGX2MizGNymq_WFuE3-MmK79n9whoVAUF8yKqvVOpSesIlDe3-uXO4Se8g0076",
    "LSOLH": "_SVI_ENL4n8Wg0I0DGBAiP01BRURIZl9xc1pWRFlGQ3JzLVFGTDFPUDdyWXpURFdvdHc4WmhReEVUekZETXBTeUNkSmZ4T1dxcVdBRXVvVQ_:29146381:59bb",
    "ndus": "YSyjrX1peHuiXFa2LLDR0ekcvnhZbA5ajPOzHTjn",
    "ndut_fmt": "DDA729563DEE372E12E3A3D1974A128BCB93D5FBC3E7586928BC7A805F45DBAA",
    "NID": "525=WBhu7ezcGdySLWv_x5IG7Y5LvOXDfkiFzmxJPfdXClXyUtXrF9AhnrppDsNPb_I5x_rmFB6y1FfVwnIZ6VhfXKgDOw1MsHkiJ4GtUrT2iotEiDCNzRML8RtNqqKlmaITloglgSsP5dtV5-jx2wcxBRV4QvdVpZd8mNbklZB3aWjnwlE_1V-JppDiZ2Z_k7SHbp_mnnubjvLApJex5h9_NhjGhcW_gy1gx86iTRGuW8dC95QDAieqHipPdTznIx1QgICeX0gdKD4q-Nwihsx6DmJXuBTac1KcWF6Y_wgIB0zh5tuBm-2pHc9TLpTX1WKXfC4a-adaCOQqj-_79SgzVItteGWFqw_OXrgOKqTk6rqUUkR__MStErtHsBHJtJZq_wyAgVXgO-co1XZMiHk_OcVh-PA1b-qFAN-omRGOjH2BGf6HYoCYD8nXqTAO4uPRvwLSXpXVlXuwOPfpI3JlDR5qECGMJd6ehqKvJVby2hV9uyh_csT_b9FNYYLVaAM47q4BICPCpcaTd9fDB1MbPBZByEVzsMXBUAM1PG-Ytphr1uHmvDuCWr1rckiFtK80ReFIHS41KJuLwHJkZTV3PJZBWTe3B_Rrje18P0e96xtTLV9LE5EuR6PrEcWPhkki7Fmk_Q5bDct8mBePCmIXrbiSpaRtF0OsmiX7zmuVvghbDaFPR1X7XWh04ydoLDfPQHMgBQmGiaySpUEXAsC_CDYua4giwaw2xMwIHrTsMzSUGuN_CT-sbWI9E4pd5ibMn4rolM9QdcMCi4aWh4eSCnxWs1ouXzH_RtJIoRIjS9jv-fsraEOHg1CkOdCV9CcFDXtTHymOM6q0pXg36Q2cv9irJUl09z7Y9Q1Ky-JFQSh4AUtHAZ_CcdcWyc_E5EsTU8NAvLK7ArR10PpXzFDUnJ8KwchajTQetUNXVZLa4sHviqodGovNdWtPx6fcWqjpDUqTQ4_4GDSSfOEwN_6Ejf7f0gxwQbhm7bd32adAW5yyabV1nAhLC6H2raQsgNCCaKYYYxzRjNTTg-jvBsT8cTUtWLAWp5-fDq4mvPqgor5F0FU",
    "OTZ": "8208315_34_34__34_",
    "PANWEB": "1",
    "SAPISID": "JIhS06pcRbNJ_7HE/ATyJLM-mzEZmSnAh7",
    "SEARCH_SAMESITE": "CgQIvJ4B",
    "SID": "g.a0000AgjDIVLA3FT_UH3JL4DGk6-wMxZd064x4bnKPrpRAhKzNe_pDlpyvkxMBd-apwpDVnmpQACgYKAbYSARcSFQHGX2MiyjX1Ixwn4W5VdbCmhlHF7hoVAUF8yKp1_rfHruhyn1czDc3Q85uB0076",
    "SIDCC": "AKEyXzWmJ5-4y9GLmwkDi-2LjC8o0h9KQL65xvKABskwvRyGemXOR4tEyDOZbYg-QyZ9ve49Dw",
    "SMSV": "ADHTe-D5UBHHfVWq1XhgQlgPGngUXYBzx5Y6JjiJikjO5VC590N2BuuYlUB5H1j61loUT4wbeBersyyVplwNG9n9ZuGqONl8v6aueo0i3E3P5sot4IIYaNzrrw9lJYHtK8IqPFAX6U8ju-Pgg6671uVyGG6bROwehw",
    "SSID": "Aa07lsLhpbcBfVr2f",
    "TSID_terabox": "EKrHlY4rFrQXQmbpdntjoIUPovGL6Oeo",
    "TSID_1024tera": "nRUDAK48xNGrKJwAf8mGVrioZ8uiEMbZ",
}

# Cookie string + dict
cookie_string = "; ".join([f"{k}={v}" for k, v in PREMIUM_COOKIES.items()])


def parse_cookies(cookie_string):
    cookies_dict = {}
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies_dict[key] = value
    return cookies_dict


# Final headers (with cookies)
HEADERS = BASE_HEADERS.copy()
HEADERS['Cookie'] = cookie_string


# --- Resolve to final URL (d8.freeterabox.com) ---
def resolve_final_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, allow_redirects=False, timeout=15)
        if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
            return resp.headers.get("Location", url)
        return url
    except Exception as e:
        logger.warning(f"Failed to resolve {url}: {e}")
        return url


# --- Fetch initial page and tokens ---
def fetch_initial_page(share_url):
    logger.info(f"Fetching initial page: {share_url}")
    parsed_cookies = parse_cookies(cookie_string)
    parsed_share_url = urlparse(share_url)
    initial_headers = BASE_HEADERS.copy()
    initial_headers['Referer'] = f"{parsed_share_url.scheme}://{parsed_share_url.netloc}/"

    response = requests.get(share_url, headers=initial_headers, cookies=parsed_cookies, timeout=20)
    response.raise_for_status()
    html = response.text

    js_token_match = re.search(r'fn%28%22([0-9A-Fa-f]+)%22%29', html)
    js_token = js_token_match.group(1) if js_token_match else None

    log_id_match = re.search(r'dp-logid=([0-9]+)', html)
    log_id = log_id_match.group(1) if log_id_match else None
    if not log_id:
        log_id_json = re.search(r'"log_id"\s*:\s*"([0-9]+)"', html)
        log_id = log_id_json.group(1) if log_id_json else None

    final_url_parsed = urlparse(response.url)
    surl_params = parse_qs(final_url_parsed.query)
    surl = surl_params.get('surl', [None])[0]

    if not js_token or not log_id or not surl:
        raise Exception(f"Missing tokens: js_token={js_token}, dp_logid={log_id}, surl={surl}")

    return {"js_token": js_token, "dp_logid": log_id, "surl": surl}


# --- Fetch file list from API ---
def fetch_file_list(js_token, dp_logid, surl, dir_path='/'):
    file_list_api_url = "https://dm.1024tera.com/share/list"
    parsed_cookies = parse_cookies(cookie_string)

    params = {
        'app_id': '250528',
        'web': '1',
        'channel': 'dubox',
        'clienttype': '0',
        'jsToken': js_token,
        'dp-logid': dp_logid,
        'page': '1',
        'num': '1000',
        'by': 'name',
        'order': 'asc',
        'site_referer': f"https://dm.1024tera.com/sharing/link?surl={surl}&clearCache=1",
        'shorturl': surl,
    }

    if dir_path == '/':
        params['root'] = '1'
    else:
        params['dir'] = dir_path
        params.pop('root', None)

    current_headers = BASE_HEADERS.copy()
    current_headers['Referer'] = params['site_referer']

    response = requests.get(file_list_api_url, headers=current_headers, cookies=parsed_cookies, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    if data.get('errno') != 0:
        raise Exception(f"API Error: {data.get('errmsg')}")

    file_items = []
    for item in data.get('list', []):
        raw_url = item.get("dlink")
        resolved_url = resolve_final_url(raw_url) if raw_url else None

        file_items.append({
            "file_name": item.get("server_filename"),
            "path": item.get("path"),
            "size": item.get("size", 0),
            "size_bytes": item.get("size", 0),
            "download_url": resolved_url,   # ✅ return final d8 link
            "is_directory": item.get("isdir", 0) == 1,
            "modify_time": item.get("server_mtime"),
            "thumbnails": item.get("thumbs", {}),
        })
    return file_items


# --- Process shared content recursively ---
def process_shared_content(share_url):
    processed_content = []
    tokens = fetch_initial_page(share_url)
    js_token = tokens['js_token']
    dp_logid = tokens['dp_logid']
    surl = tokens['surl']

    root_items = fetch_file_list(js_token, dp_logid, surl, dir_path='/')

    def traverse_items(items_list):
        for item in items_list:
            if item['is_directory']:
                sub_items = fetch_file_list(js_token, dp_logid, surl, dir_path=item['path'])
                traverse_items(sub_items)
            else:
                processed_content.append(item)

    traverse_items(root_items)
    return processed_content


# --- Flask Route ---
@app.route("/terabox/fetch", methods=["GET"])
def fetch():
    share_url = request.args.get("url")
    if not share_url:
        return jsonify({
            "status": "error",
            "message": "Missing ?url parameter",
            "developer": "bhookibhabhi"
        }), 400

    try:
        results = process_shared_content(share_url)
        return jsonify({
            "status": "success",
            "files": results,
            "developer": "bhookibhabhi"
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "developer": "bhookibhabhi"
        }), 500

# --- Run Flask Server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)