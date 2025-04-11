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
            stream=True,
            timeout=10
        )

        excluded_headers = ['Transfer-Encoding', 'Connection', 'Content-Encoding', 'Content-Length']
        response_headers = {key: value for key, value in response.headers.items()
                            if key not in excluded_headers}

        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        content_length = response.headers.get('Content-Length')

        return Response(
            response.iter_content(chunk_size=8192),
            status=response.status_code,
            headers={
                **response_headers,
                'Content-Type': content_type,
                'Content-Length': content_length or str(len(response.content))
            }
        )

    except requests.RequestException as e:
        return Response(f"Error: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7812)
