from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Mapeo de las API externas
API_MAPPING = {
    'api1': 'https://api.test2.com',
    'api2': 'https://api.test3.com',

}

@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
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