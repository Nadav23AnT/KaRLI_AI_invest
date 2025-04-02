import os

from server.app import app

LISTEN_HOST = os.environ.get('LISTEN_HOST', 'localhost')
LISTEN_PORT = os.environ.get('LISTEN_PORT', '5000')

if __name__ == '__main__':
    app.run(debug=True, host=LISTEN_HOST, port=LISTEN_PORT)
