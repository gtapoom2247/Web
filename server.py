#!/usr/bin/env python3
"""ระบบติดตามบัตร พขร. — Server ใช้ SheetDB เก็บข้อมูล"""

import http.server, json, os, webbrowser, urllib.parse, sys, requests
from datetime import datetime

SDB_V = 'https://sheetdb.io/api/v1/7kug67yp5gt6p'
SDB_D = 'https://sheetdb.io/api/v1/4gmyhp9rtkbcn'

V_HEADERS = [
    'เบอร์รถ', 'จังหวัด', 'ทะเบียนหัว', 'ทะเบียนหาง',
    'ธพน.2 วันออกบัตร', 'ธพน.2 หมดอายุบัตร',
    'ภาษี วันออกบัตร', 'ภาษี หมดอายุบัตร',
    'Thaioil SRC วันออกบัตร', 'Thaioil SRC หมดอายุบัตร',
    'Esso SRC วันออกบัตร', 'Esso SRC หมดอายุบัตร',
    'PTT-GC วันออกบัตร', 'PTT-GC หมดอายุบัตร',
    'LLK Thappline วันออกบัตร', 'LLK Thappline หมดอายุบัตร',
    'SRB Thappline วันออกบัตร', 'SRB Thappline หมดอายุบัตร',
    'SPRC วันออกบัตร', 'SPRC หมดอายุบัตร',
    'IRPC IRY & AU วันออกบัตร', 'IRPC IRY & AU หมดอายุบัตร',
    'วันเวลาล่าสุด',
]

D_HEADERS = [
    'id', 'เบอร์รถ', 'ชื่อ', 'เบอร์โทร',
    'Esso SRC วันออกบัตร', 'Esso SRC หมดอายุบัตร',
    'PTT-GC วันออกบัตร', 'PTT-GC หมดอายุบัตร',
    'LLK Thappline วันออกบัตร', 'LLK Thappline หมดอายุบัตร',
    'SRB Thappline วันออกบัตร', 'SRB Thappline หมดอายุบัตร',
    'SPRC วันออกบัตร', 'SPRC หมดอายุบัตร',
    'Thaioil SRC วันออกบัตร', 'Thaioil SRC หมดอายุบัตร',
    'IRPC IRY & AU วันออกบัตร', 'IRPC IRY & AU หมดอายุบัตร',
    'วันเวลาล่าสุด',
]

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(DIR, 'Index.html')
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def sdb_get(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=15).json()
    except Exception as e:
        print(f'  [sdb_get error] {e}')
        return []


def sdb_post(url, data):
    try:
        r = requests.post(url, json={'data': data}, headers=HEADERS, timeout=15)
        return r.status_code in (200, 201)
    except Exception as e:
        print(f'  [sdb_post error] {e}')
        return False


def sdb_put(url, col, val, data):
    try:
        encoded = urllib.parse.quote(str(val), safe='')
        r = requests.put(
            f'{url}/{urllib.parse.quote(col, safe="")}/{encoded}',
            json={'data': data},
            headers=HEADERS,
            timeout=15,
        )
        return r.status_code == 200
    except Exception as e:
        print(f'  [sdb_put error] {e}')
        return False


def sdb_delete(url, col, val):
    try:
        encoded = urllib.parse.quote(str(val), safe='')
        requests.delete(
            f'{url}/{urllib.parse.quote(col, safe="")}/{encoded}',
            headers=HEADERS,
            timeout=15,
        )
    except Exception as e:
        print(f'  [sdb_delete error] {e}')


def now_str():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


class Handler(http.server.BaseHTTPRequestHandler):

    def _send(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html):
        body = html.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length:
            try:
                return json.loads(self.rfile.read(length))
            except Exception:
                pass
        return {}

    def do_OPTIONS(self):
        self._send({})

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == '/':
            try:
                with open(HTML, 'r', encoding='utf-8') as f:
                    self._send_html(f.read())
            except FileNotFoundError:
                self._send({'error': 'Index.html not found'}, 500)

        elif path == '/api/vehicles':
            self._send(sdb_get(SDB_V))

        elif path.startswith('/api/vehicles/'):
            ber = urllib.parse.unquote(path.split('/')[-1])
            rows = sdb_get(f'{SDB_V}?search={urllib.parse.quote("เบอร์รถ")}={urllib.parse.quote(ber)}')
            self._send(rows[0] if rows else {'error': 'not found'}, 200 if rows else 404)

        elif path == '/api/drivers':
            self._send(sdb_get(SDB_D))

        elif path.startswith('/api/drivers/'):
            rid = urllib.parse.unquote(path.split('/')[-1])
            rows = sdb_get(f'{SDB_D}?search=id={urllib.parse.quote(rid)}')
            self._send(rows[0] if rows else {'error': 'not found'}, 200 if rows else 404)

        else:
            self._send({'error': 'not found'}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        body = self._read_body()
        items = body.get('data', body)
        if isinstance(items, dict):
            items = [items]

        if path == '/api/vehicles':
            created = 0
            for item in items:
                ber = item.get('เบอร์รถ', '').strip()
                if not ber:
                    continue
                item['วันเวลาล่าสุด'] = now_str()
                exist = sdb_get(
                    f'{SDB_V}?search={urllib.parse.quote("เบอร์รถ")}={urllib.parse.quote(ber)}'
                )
                if exist:
                    merged = exist[0]
                    for h in V_HEADERS:
                        if h in item:
                            merged[h] = item[h]
                    sdb_put(SDB_V, 'เบอร์รถ', ber, merged)
                else:
                    sdb_post(SDB_V, item)
                    created += 1
            self._send({'created': str(created)})

        elif path == '/api/drivers':
            created = 0
            for item in items:
                phone = item.get('เบอร์โทร', '').strip()
                item['วันเวลาล่าสุด'] = now_str()

                if phone:
                    exist = sdb_get(
                        f'{SDB_D}?search={urllib.parse.quote("เบอร์โทร")}={urllib.parse.quote(phone)}'
                    )
                    if exist:
                        merged = exist[0]
                        for h in D_HEADERS:
                            if h in item:
                                merged[h] = item[h]
                        sdb_put(SDB_D, 'เบอร์โทร', phone, merged)
                        continue

                # หาค่า id สูงสุด แล้ว +1
                all_rows = sdb_get(SDB_D)
                max_id = 0
                for row in all_rows:
                    try:
                        max_id = max(max_id, int(row.get('id', 0)))
                    except (ValueError, TypeError):
                        pass
                item['id'] = str(max_id + 1)
                sdb_post(SDB_D, item)
                created += 1

            self._send({'created': str(created)})

        else:
            self._send({'error': 'not found'}, 404)

    def do_PUT(self):
        path = urllib.parse.urlparse(self.path).path
        body = self._read_body()
        data = body.get('data', body)

        if path.startswith('/api/vehicles/'):
            ber = urllib.parse.unquote(path.split('/')[-1])
            data['วันเวลาล่าสุด'] = now_str()
            sdb_put(SDB_V, 'เบอร์รถ', ber, data)
            self._send({'updated': '1'})

        elif path.startswith('/api/drivers/'):
            rid = urllib.parse.unquote(path.split('/')[-1])
            data['id'] = rid
            data['วันเวลาล่าสุด'] = now_str()
            sdb_put(SDB_D, 'id', rid, data)
            self._send({'updated': '1'})

        else:
            self._send({'error': 'not found'}, 404)

    def do_DELETE(self):
        path = urllib.parse.urlparse(self.path).path

        if path.startswith('/api/vehicles/'):
            ber = urllib.parse.unquote(path.split('/')[-1])
            sdb_delete(SDB_V, 'เบอร์รถ', ber)
            self._send({'deleted': '1'})

        elif path.startswith('/api/drivers/'):
            rid = urllib.parse.unquote(path.split('/')[-1])
            sdb_delete(SDB_D, 'id', rid)
            self._send({'deleted': '1'})

        else:
            self._send({'error': 'not found'}, 404)

    def log_message(self, fmt, *args):
        sys.stderr.write(f'  [{args[0]}] {args[1]} {args[2]}\n')


if __name__ == '__main__':
    srv = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    url = f'http://localhost:{PORT}'
    print(f'\n  ** เปิดเบราว์เซอร์ที่: {url}')
    print(f'  ** ข้อมูลบันทึกลง Google Sheets ผ่าน SheetDB')
    print(f'  ** กด Ctrl+C เพื่อปิดเซิร์ฟเวอร์\n')
    webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n  ** ปิดเซิร์ฟเวอร์แล้ว\n')
        srv.shutdown()
