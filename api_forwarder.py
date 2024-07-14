from flask import Flask, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import argparse

app = Flask(__name__)

# Inicializar argumentos
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--RateLimit", default="10000", help="Rate Limit per second")
args = parser.parse_args()

if args.RateLimit:
    print("Rate Limit: % s" % args.RateLimit)

# Setup limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per second"],
    storage_uri="memory://"
)

# Mapeo de las API externas
API_MAPPING = {
    'fact': 'https://catfact.ninja',
    'api2': 'https://api.test3.com',

}

@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit(f"{args.RateLimit} per second")
def forward_request(subpath):
    # Obtener el destino a partir del path
    destination = subpath.split('/')[0]
    if destination not in API_MAPPING:
        return "Invalid path", 404
    
    # Nueva URL
    new_url = f"{API_MAPPING[destination]}/{subpath}"

    # Forward el request
    resp = requests.request(
        method=request.method,
        url=new_url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    # Flask Response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)