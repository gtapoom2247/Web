#!/usr/bin/env python3
"""ระบบติดตามบัตร พขร. — Server ใช้ SheetDB เก็บข้อมูล"""

import http.server, json, os, webbrowser, urllib.parse, sys, requests
from datetime import datetime

SDB_V = 'https://sheetdb.io/api/v1/7kug67yp5gt6p'
SDB_D = 'https://sheetdb.io/api/v1/4gmyhp9rtkbcn'

V_HEADERS = ['เบอร์รถ','จังหวัด','ทะเบียนหัว','ทะเบียนหาง',
             'ธพน.2 วันออกบัตร','ธพน.2 หมดอายุบัตร','ภาษี วันออกบัตร','ภาษี หมดอายุบัตร',
             'Thaioil SRC วันออกบัตร','Thaioil SRC หมดอายุบัตร',
             'Esso SRC วันออกบัตร','Esso SRC หมดอายุบัตร',
             'PTT-GC วันออกบัตร','PTT-GC หมดอายุบัตร',
             'LLK Thappline วันออกบัตร','LLK Thappline หมดอายุบัตร',
             'SRB Thappline วันออกบัตร','SRB Thappline หมดอายุบัตร',
             'SPRC วันออกบัตร','SPRC หมดอายุบัตร',
             'IRPC IRY & AU วันออกบัตร','IRPC IRY & AU หมดอายุบัตร']

D_HEADERS = ['id','เบอร์รถ','ชื่อ','เบอร์โทร',
             'Esso SRC วันออกบัตร','Esso SRC หมดอายุบัตร',
             'PTT-GC วันออกบัตร','PTT-GC หมดอายุบัตร',
             'LLK Thappline วันออกบัตร','LLK Thappline หมดอายุบัตร',
             'SRB Thappline วันออกบัตร','SRB Thappline หมดอายุบัตร',
             'SPRC วันออกบัตร','SPRC หมดอายุบัตร',
             'Thaioil SRC วันออกบัตร','Thaioil SRC หมดอายุบัตร',
             'IRPC IRY & AU วันออกบัตร','IRPC IRY & AU หมดอายุบัตร',
             'วันเวลาล่าสุด']

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(DIR, 'Index.html')
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def sdb_get(url):
    try: return requests.get(url, headers=HEADERS, timeout=15).json()
    except: return []

def sdb_post(url, data):
    try:
        r = requests.post(url, json={'data': data}, headers=HEADERS, timeout=15)
        return r.status_code in (200, 201)
    except: return False

def sdb_put(url, col, val, data):
    try:
        r = requests.put(f'{url}/{col}/{val}', json={'data': data}, headers=HEADERS, timeout=15)
        return r.status_code == 200
    except: return False

def sdb_delete(url, col, val):
    try:
        requests.delete(f'{url}/{col}/{val}', headers=HEADERS, timeout=15)
    except: pass

class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())

    def do_OPTIONS(self):
        self._send({})

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == '/':
            try:
                with open(HTML, 'r', encoding='utf-8') as f:
                    self._send_html(f.read())
            except:
                self._send({'error': 'Index.html not found'}, 500)
        elif path == '/api/vehicles':
            self._send(sdb_get(SDB_V))
        elif path.startswith('/api/vehicles/'):
            ber = urllib.parse.quote(path.split('/')[-1])
            rows = sdb_get(f'{SDB_V}?search=เบอร์รถ={ber}')
            self._send(rows[0] if rows else {'error': 'not found'}, 200 if rows else 404)
        elif path == '/api/drivers':
            self._send(sdb_get(SDB_D))
        elif path.startswith('/api/drivers/'):
            rid = path.split('/')[-1]
            rows = sdb_get(f'{SDB_D}?search=id={rid}')
            self._send(rows[0] if rows else {'error': 'not found'}, 200 if rows else 404)
        else:
            self._send({'error': 'not found'}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        items = body.get('data', body)
        if isinstance(items, dict): items = [items]

        if path == '/api/vehicles':
            n = 0
            for item in items:
                ber = item.get('เบอร์รถ', '')
                if not ber: continue
                q = urllib.parse.quote(ber)
                exist = sdb_get(f'{SDB_V}?search=เบอร์รถ={q}')
                if exist:
                    for h in V_HEADERS:
                        if h in item: exist[0][h] = item[h]
                    sdb_put(SDB_V, 'เบอร์รถ', ber, exist[0])
                else:
                    sdb_post(SDB_V, item)
                    n += 1
            self._send({'created': str(n)})

        elif path == '/api/drivers':
            n = 0
            for item in items:
                phone = item.get('เบอร์โทร', '')
                if phone:
                    q = urllib.parse.quote(phone)
                    exist = sdb_get(f'{SDB_D}?search=เบอร์โทร={q}')
                    if exist:
                        r = exist[0]
                        for h in D_HEADERS:
                            if h in item: r[h] = item[h]
                        r['วันเวลาล่าสุด'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        sdb_put(SDB_D, 'เบอร์โทร', phone, r)
                        continue
                all_rows = sdb_get(SDB_D)
                max_id = 0
                for r in all_rows:
                    try: max_id = max(max_id, int(r.get('id', 0)))
                    except: pass
                item['id'] = str(max_id + 1)
                item['วันเวลาล่าสุด'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                sdb_post(SDB_D, item)
                n += 1
            self._send({'created': str(n)})

    def do_PUT(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        data = body.get('data', body)

        if path.startswith('/api/vehicles/'):
            ber = path.split('/')[-1]
            sdb_put(SDB_V, 'เบอร์รถ', ber, data)
            self._send({'updated': '1'})
        elif path.startswith('/api/drivers/'):
            rid = path.split('/')[-1]
            data['id'] = rid
            sdb_put(SDB_D, 'id', rid, data)
            self._send({'updated': '1'})
        else:
            self._send({'error': 'not found'}, 404)

    def log_message(self, fmt, *a):
        sys.stderr.write(f'  [{a[0]}] {a[1]} {a[2]}\n')

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
