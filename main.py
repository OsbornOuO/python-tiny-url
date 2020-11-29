from flask import Flask
from app import create_app
import os

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app = create_app()

    port = int(os.environ.get('PORT', 17995))
    app.run(host='0.0.0.0', port=port)
