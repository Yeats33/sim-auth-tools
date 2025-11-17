#!/usr/bin/env python3
import os
import requests
import random
import string
import json

IDATARIVER_HOST = "https://open.idatariver.com"
DEVELOPER_SECRET = os.environ.get('DEVELOPER_SECRET')
CF_ACCOUNT_ID = os.environ.get('CF_ACCOUNT_ID')
CF_API_TOKEN = os.environ.get('CF_API_TOKEN')
NAMESPACE_ID = os.environ.get('CODES_NAMESPACE_ID')

def generate_code(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def query_license(codes):
    url = f"{IDATARIVER_HOST}/mapi/license/query"
    headers = {"Authorization": f"Bearer {DEVELOPER_SECRET}"}
    params = {"code": ",".join(codes)}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def activate_license(codes):
    url = f"{IDATARIVER_HOST}/mapi/license/activate"
    headers = {"Authorization": f"Bearer {DEVELOPER_SECRET}"}
    data = {"code": ",".join(codes)}
    r = requests.post(url, headers=headers, data=data, timeout=10)
    r.raise_for_status()
    return r.json()

def upload_codes_to_kv(codes, code_type, days):
    for code in codes:
        key = code
        value = json.dumps({"type": code_type, "days": days, "used_by": None})
        url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE_ID}/values/{key}"
        headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
        res = requests.put(url, headers=headers, data=value)
        if not res.ok:
            print(f"Failed to upload {code}: {res.text}")
        else:
            print(f"Uploaded {code}")

def main():
    # Example usage generating codes and uploading them.
    num = int(os.environ.get('NUM_CODES', '10'))
    code_type = os.environ.get('CODE_TYPE', 'trial')
    days = int(os.environ.get('DAYS', '14'))
    codes = [generate_code() for _ in range(num)]
    upload_codes_to_kv(codes, code_type, days)
    print('Generated and uploaded codes:', codes)

if __name__ == "__main__":
    main()
