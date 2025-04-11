from flask import Flask, request, Response
import requests

app = Flask(__name__)

VK_API_URL = "https://api.vk.com"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    print("\n--- Incoming Request ---")
    print(f"Method: {request.method}")
    print(f"Path: /{path}")
    print(f"Query Params: {request.args}")
    print("Headers:")
    for key, value in request.headers.items():
        print(f"  {key}: {value}")
    print("Body:")
    try:
        print(request.get_data(as_text=True))
    except Exception as e:
        print(f"  [Error reading body: {e}]")
    print("--- End of Request ---\n")

    target_url = f"{VK_API_URL}/{path}"
    query_params = request.args.to_dict(flat=False)
    headers = dict(request.headers)
    headers.pop('Host', None)
    body = request.get_data()

    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            params=query_params,
            headers=headers,
            data=body,
            stream=False,
            timeout=10
        )

        response_headers = dict(response.headers)
        for header in ['Transfer-Encoding', 'Connection', 'Content-Encoding']:
            response_headers.pop(header, None)

        return Response(
            response.content,
            status=response.status_code,
            headers=response_headers
        )

    except requests.RequestException as e:
        return Response(f"Error: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7812)
