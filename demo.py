"""Run real milestone tests and keep three TCP clients connected for evidence."""
import concurrent.futures
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)


def connect(port):
    for _ in range(100):
        try:
            return socket.create_connection(('127.0.0.1', port), timeout=3)
        except ConnectionRefusedError:
            time.sleep(.1)
    raise RuntimeError('Server did not start')


class Client:
    def __init__(self, name):
        self.name = name
        self.socket = connect(5008)
        self.reader = self.socket.makefile('r', encoding='utf-8')
        self.log = []

    def request(self, **message):
        self.socket.sendall((json.dumps(message) + '\n').encode())
        response = json.loads(self.reader.readline())
        self.log.extend(['SEND ' + json.dumps(message), 'RECV ' + json.dumps(response)])
        return response


def main():
    week6 = subprocess.Popen([sys.executable, '-u', str(ROOT / 'week6/server.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with connect(5006) as connection:
        message = 'Hello from The Socket Scientists!'
        connection.sendall((message + '\n').encode())
        reply = connection.makefile('r', encoding='utf-8').readline().strip()
        assert reply == 'Hello client! Server received: ' + message
    week6_log = week6.communicate(timeout=5)[0]
    client6_log = f'Connected to 127.0.0.1:5006\nSent: {message}\nReceived: {reply}\nPASS: exact response received'
    (EVIDENCE / 'week6.txt').write_text(week6_log + '\nCLIENT\n' + client6_log, encoding='utf-8')

    server = subprocess.Popen([sys.executable, '-u', str(ROOT / 'week8/server.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    server_lines = []
    def capture():
        for line in server.stdout:
            server_lines.append(line.rstrip())
    threading.Thread(target=capture, daemon=True).start()
    clients = [Client(name) for name in ('Hamza', 'Zackaria', 'Haroon')]
    results = []
    try:
        for client in clients:
            assert client.request(type='JOIN', client_id=client.name)['status'] == 'joined'
        status = clients[0].request(type='STATUS')
        assert status['active_clients'] == 3
        results.append('PASS: three clients joined and remain connected simultaneously')
        assert clients[0].request(type='PING', message='Week 8 hello')['message'] == 'Week 8 hello'
        barrier = threading.Barrier(2)
        def compete(client):
            barrier.wait()
            return client.request(type='BOOK', seat='A1')['status']
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            outcomes = list(pool.map(compete, clients[:2]))
        assert sorted(outcomes) == ['already_taken', 'booked']
        results.append('PASS: simultaneous A1 requests produced exactly one booked and one already_taken')
        assert clients[2].request(type='BOOK', seat='A2')['status'] == 'booked'
        assert clients[2].request(type='BOOK', seat='A2')['status'] == 'already_booked'
        assert clients[2].request(type='MY_BOOKING')['seats'] == ['A2']
        available = clients[2].request(type='LIST')['available']
        assert 'A1' not in available and 'A2' not in available
        results.append('PASS: different seat, repeated booking, availability and own-booking checks')
        assert clients[2].request(type='BOOK', seat='Z99')['status'] == 'error'
        assert clients[2].request(type='UNKNOWN')['status'] == 'error'
        guest = Client('guest')
        assert guest.request(type='LIST')['message'] == 'JOIN first'
        assert guest.request(type='JOIN', client_id='Hamza')['status'] == 'error'
        guest.socket.sendall(b'not json\n')
        assert json.loads(guest.reader.readline())['status'] == 'error'
        guest.reader.close()
        guest.socket.close()
        results.append('PASS: invalid seat, unknown command, join-first, duplicate ID and malformed JSON rejected')
        for client in clients:
            assert client.request(type='STATUS')['active_clients'] == 3
        time.sleep(.2)
        text = '\n'.join(results) + '\n\nSERVER\n' + '\n'.join(server_lines)
        for client in clients:
            text += '\n\nCLIENT ' + client.name + '\n' + '\n'.join(client.log)
        (EVIDENCE / 'week8.txt').write_text(text, encoding='utf-8')
        (EVIDENCE / 'test-results.txt').write_text('Week 6: PASS\n' + '\n'.join(results), encoding='utf-8')

        app = tk.Tk()
        app.title('The Socket Scientists - Phase 2 - Live TCP Evidence')
        app.geometry('1400x900')
        app.configure(bg='#e9edf4')
        tk.Label(app, text='SE 239 | The Socket Scientists | Phase 2', font=('Arial', 19, 'bold'), bg='#e9edf4').pack(pady=8)
        tk.Label(app, text='Real Python TCP sockets on localhost | Week 6 exchange passed | Week 8: 3 clients connected', bg='#e9edf4', font=('Arial', 12)).pack()
        area = tk.Frame(app)
        area.pack(fill='both', expand=True, padx=12, pady=10)
        def panel(row, col, heading, content):
            frame = tk.LabelFrame(area, text=heading, font=('Arial', 12, 'bold'))
            frame.grid(row=row, column=col, sticky='nsew', padx=4, pady=4)
            box = ScrolledText(frame, wrap='word', font=('Consolas', 10), height=10, width=50)
            box.pack(fill='both', expand=True)
            box.insert('end', content)
            box.configure(state='disabled')
            return box
        for i in range(2):
            area.rowconfigure(i, weight=1)
            area.columnconfigure(i, weight=1)
        panel(0, 0, 'Week 6: server and client', week6_log + '\nCLIENT\n' + client6_log)
        panel(0, 1, 'Week 8: server / verification', '\n'.join(results) + '\n\n' + '\n'.join(server_lines[:12]))
        panel(1, 0, 'Week 8: clients 1 and 2 - Hamza / Zackaria', '\n'.join(clients[0].log + ['\nCLIENT 2: Zackaria'] + clients[1].log))
        panel(1, 1, 'Week 8: client 3 - Haroon', '\n'.join(clients[2].log))
        tk.Label(app, text='Evidence viewer uses separate server processes and three persistent client sockets. Close to disconnect.', bg='#e9edf4').pack(pady=5)
        app.mainloop()
    finally:
        for client in clients:
            client.reader.close()
            client.socket.close()
        server.terminate()
        server.wait(timeout=5)


if __name__ == '__main__':
    main()
