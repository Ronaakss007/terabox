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

# --- Headers ---
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    'Accept': "application/json, text/plain, */*",
    'Accept-Encoding': "identity",
    'X-Requested-With': "XMLHttpRequest",
    'Content-Type': "application/x-www-form-urlencoded",
}

# --- Premium Cookies ---
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
COOKIE_STRING = "; ".join([f"{k}={v}" for k,v in PREMIUM_COOKIES.items()])
COOKIES_DICT = {k:v for k,v in (cookie.split('=',1) for cookie in COOKIE_STRING.split('; ') if '=' in cookie)}

# --- Fetch initial tokens ---
def fetch_tokens(share_url):
    logger.info(f"Fetching tokens for: {share_url}")
    resp = requests.get(share_url, headers=HEADERS, cookies=COOKIES_DICT, timeout=30)
    resp.raise_for_status()
    html = resp.text

    js_token = re.search(r'fn%28%22([0-9A-Fa-f]+)%22%29', html)
    js_token = js_token.group(1) if js_token else None

    dp_logid = re.search(r'"log_id"\s*:\s*"([0-9]+)"', html)
    if not dp_logid:
        dp_logid = re.search(r'dp-logid=([0-9]+)', html)
    dp_logid = dp_logid.group(1) if dp_logid else None

    surl = parse_qs(urlparse(resp.url).query).get('surl', [None])[0]

    if not js_token or not dp_logid or not surl:
        logger.error(f"Failed to extract tokens: js_token={js_token}, dp_logid={dp_logid}, surl={surl}")
        raise Exception("Unable to extract necessary tokens")

    return js_token, dp_logid, surl

# --- Fetch files from API ---
def fetch_file_list(js_token, dp_logid, surl, dir_path='/'):
    api_url = "https://dm.1024tera.com/share/list"
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
        'shorturl': surl
    }
    if dir_path == '/':
        params['root'] = '1'
    else:
        params['dir'] = dir_path

    resp = requests.get(api_url, headers=HEADERS, cookies=COOKIES_DICT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get('errno') != 0:
        raise Exception(f"API Error: {data.get('errmsg')}")

    files = []
    for item in data.get('list', []):
        files.append({
            "file_name": item.get("server_filename"),
            "path": item.get("path"),
            "size": item.get("size", 0),
            "download_url": item.get("dlink"),
            "is_directory": item.get("isdir", 0) == 1,
            "modify_time": item.get("server_mtime"),
            "thumbnails": item.get("thumbs", {})
        })
    return files

# --- Resolve final link safely ---
def resolve_final_link(dlink):
    if not dlink:
        return None
    try:
        # Use HEAD to resolve redirect without downloading
        resp = requests.head(dlink, headers=HEADERS, cookies=COOKIES_DICT, allow_redirects=True, timeout=60)
        return resp.url
    except Exception as e:
        logger.error(f"Failed to resolve dlink: {e}")
        return dlink  # fallback to original link

# --- Process folder recursively ---
def process_folder(share_url):
    js_token, dp_logid, surl = fetch_tokens(share_url)
    results = []

    def traverse(items):
        for item in items:
            if item['is_directory']:
                sub_items = fetch_file_list(js_token, dp_logid, surl, dir_path=item['path'])
                traverse(sub_items)
            else:
                final_url = resolve_final_link(item['download_url'])
                results.append({
                    "file_name": item['file_name'],
                    "path": item['path'],
                    "size": item['size'],
                    "download_url": item['download_url'],
                    "final_download_url": final_url,
                    "modify_time": item['modify_time'],
                    "thumbnails": item['thumbnails']
                })

    root_items = fetch_file_list(js_token, dp_logid, surl)
    traverse(root_items)
    return results

# --- Flask Route ---
@app.route("/terabox/fetch", methods=["GET"])
def fetch_route():
    share_url = request.args.get("url")
    if not share_url:
        return jsonify({"status":"error","message":"Missing ?url parameter"}), 400
    try:
        files = process_folder(share_url)
        return jsonify({"status":"success","files":files})
    except Exception as e:
        logger.error(str(e))
        return jsonify({"status":"error","message":str(e)}), 500

# --- Run Flask ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
