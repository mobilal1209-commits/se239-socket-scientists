"""Week 6: one TCP client exchanges a message with the server."""
import socket


def main():
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', 5006))
        server.listen(1)
        print('Week 6 server listening on 127.0.0.1:5006', flush=True)
        connection, address = server.accept()
        with connection, connection.makefile('r', encoding='utf-8') as reader:
            print(f'Client connected: {address}', flush=True)
            message = reader.readline(4096).strip()
            print(f'Received: {message}', flush=True)
            reply = f'Hello client! Server received: {message}'
            connection.sendall((reply + '\n').encode('utf-8'))
            print(f'Sent: {reply}', flush=True)


if __name__ == '__main__':
    main()
