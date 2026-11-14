"""Threaded TCP ticket server. Messages are newline-delimited JSON."""
import json
import re
import socketserver
import threading


class TicketServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address):
        super().__init__(address, ClientHandler)
        self.lock = threading.Lock()
        self.members = set()
        self.bookings = {f'A{i}': None for i in range(1, 13)}


class ClientHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.client_id = None
        print(f'CONNECTED {self.client_address}', flush=True)
        try:
            while True:
                line = self.rfile.readline(4097)
                if not line:
                    break
                if len(line) > 4096 or not line.endswith(b'\n'):
                    self.send({'status': 'error', 'message': 'Message too long or missing newline'})
                    break
                try:
                    request = json.loads(line)
                    if not isinstance(request, dict):
                        raise ValueError('Request must be an object')
                    response = self.process(request)
                except (ValueError, UnicodeDecodeError) as error:
                    response = {'status': 'error', 'message': str(error)}
                self.send(response)
                print(f'{self.client_id or "guest"}: {line.decode(errors="replace").strip()} -> {json.dumps(response)}', flush=True)
        except (ConnectionError, OSError):
            pass
        finally:
            with self.server.lock:
                self.server.members.discard(self.client_id)
                print(f'DISCONNECTED {self.client_id or "guest"}; active clients={len(self.server.members)}', flush=True)

    def send(self, response):
        self.wfile.write((json.dumps(response) + '\n').encode('utf-8'))
        self.wfile.flush()

    def process(self, request):
        command = request.get('type')
        with self.server.lock:
            if command == 'JOIN':
                name = request.get('client_id')
                if self.client_id:
                    return {'status': 'error', 'message': 'Already joined'}
                if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,32}', name):
                    return {'status': 'error', 'message': 'Use 1-32 letters, digits, underscores or hyphens'}
                if name in self.server.members:
                    return {'status': 'error', 'message': 'Client ID already connected'}
                self.client_id = name
                self.server.members.add(name)
                count = len(self.server.members)
                print(f'JOIN {name}; active clients={count}', flush=True)
                return {'status': 'joined', 'client_id': name, 'active_clients': count}
            if not self.client_id:
                return {'status': 'error', 'message': 'JOIN first'}
            if command == 'PING':
                return {'status': 'ok', 'message': request.get('message', 'Hello')}
            if command == 'STATUS':
                return {'status': 'ok', 'active_clients': len(self.server.members), 'members': sorted(self.server.members)}
            if command == 'LIST':
                return {'status': 'ok', 'available': [seat for seat, owner in self.server.bookings.items() if owner is None]}
            if command == 'MY_BOOKING':
                return {'status': 'ok', 'seats': [seat for seat, owner in self.server.bookings.items() if owner == self.client_id]}
            if command == 'BOOK':
                seat = request.get('seat')
                if not isinstance(seat, str) or seat not in self.server.bookings:
                    return {'status': 'error', 'message': 'Unknown seat'}
                owner = self.server.bookings[seat]
                if owner == self.client_id:
                    return {'status': 'already_booked', 'seat': seat}
                if owner is not None:
                    return {'status': 'already_taken', 'seat': seat}
                if self.client_id in self.server.bookings.values():
                    return {'status': 'error', 'message': 'One seat per client'}
                self.server.bookings[seat] = self.client_id
                return {'status': 'booked', 'seat': seat}
            return {'status': 'error', 'message': 'Unknown command'}


if __name__ == '__main__':
    with TicketServer(('127.0.0.1', 5008)) as server:
        print('Week 8 ticket server listening on 127.0.0.1:5008', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Server stopped', flush=True)
