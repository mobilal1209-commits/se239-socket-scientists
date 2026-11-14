"""Run after the Week 6 server."""
import socket


def main():
    with socket.create_connection(('127.0.0.1', 5006), timeout=10) as connection:
        print('Connected to 127.0.0.1:5006')
        message = 'Hello from The Socket Scientists!'
        connection.sendall((message + '\n').encode('utf-8'))
        print(f'Sent: {message}')
        with connection.makefile('r', encoding='utf-8') as reader:
            print(f'Received: {reader.readline().strip()}')


if __name__ == '__main__':
    main()
