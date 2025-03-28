import os

from server.app import app

LISTEN_HOST = os.environ['LISTEN_HOST']
LISTEN_PORT = os.environ['LISTEN_PORT']

if __name__ == '__main__':
    app.run(debug=True, host=LISTEN_HOST, port=LISTEN_PORT)
