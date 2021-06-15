#!/usr/bin/env python3

import argparse
import os
from flask import Flask, request
import requests

GATEWAY_API_TOKEN = os.getenv("STREAM_GATEWAY_TOKEN")
HOST = '0.0.0.0'
PORT = 9000
GATEWAY_URL = ''

app = Flask(__name__)


@app.route('/sessions', methods=['POST'])
def create_session():
    """
    Creates a new session. Sessions contain information about the application being streamed, display size, and metadata
    about the stream. A session can outlive its underlying Android container.
    :return:
    """
    request_data = request.get_json()
    print(request_data)
    data = {
        'app': 'my-android10-app'
    }
    headers = {'Authorization': f'macaroon root={GATEWAY_API_TOKEN}'}
    r = requests.post(f'https://{GATEWAY_URL}', data=data, headers=headers)
    if not r.ok:
        return "something went wrong"
    return ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='websocket proxy.')
    parser.add_argument('--gateway_url', help='Stream Gateway URL')
    args = parser.parse_args()
    GATEWAY_URL = args.gateway_url

    if not GATEWAY_URL:
        print('missing --gateway_url')
        exit(1)
