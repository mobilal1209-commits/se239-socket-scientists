"""Interactive client: JOIN, then list/book/my/status/ping/quit."""
import json
import socket


def main():
    name = input('Client ID: ').strip()
    try:
        with socket.create_connection(('127.0.0.1', 5008), timeout=10) as connection:
            connection.settimeout(None)
            with connection.makefile('r', encoding='utf-8') as reader:
                def request(message):
                    connection.sendall((json.dumps(message) + '\n').encode('utf-8'))
                    reply = reader.readline()
                    if not reply:
                        raise ConnectionError('Server disconnected')
                    result = json.loads(reply)
                    print(json.dumps(result, indent=2))
                    return result
                if request({'type': 'JOIN', 'client_id': name}).get('status') != 'joined':
                    return
                print('Commands: list | book A1 | my | status | ping hello | quit')
                while True:
                    parts = input('> ').strip().split(maxsplit=1)
                    if not parts:
                        continue
                    command = parts[0].lower()
                    if command == 'quit':
                        break
                    if command == 'book' and len(parts) == 2:
                        request({'type': 'BOOK', 'seat': parts[1].upper()})
                    elif command == 'ping':
                        request({'type': 'PING', 'message': parts[1] if len(parts) == 2 else 'Hello'})
                    elif command in ('list', 'my', 'status'):
                        request({'type': {'list': 'LIST', 'my': 'MY_BOOKING', 'status': 'STATUS'}[command]})
                    else:
                        print('Use list, book A1, my, status, ping hello, or quit')
    except (OSError, ValueError, ConnectionError) as error:
        print(f'Connection error: {error}')


if __name__ == '__main__':
    main()
