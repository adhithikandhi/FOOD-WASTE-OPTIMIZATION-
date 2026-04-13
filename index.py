from app import app
from werkzeug.wsgi import make_environ

def handler(request):
    # Create WSGI environ from Vercel request
    environ = make_environ(request.method, request.url, request.data, request.headers)
    environ['wsgi.input'] = request.data
    environ['wsgi.errors'] = None
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = False
    environ['wsgi.run_once'] = False

    # Collect response
    response_data = []
    response_headers = []
    status_code = [200]

    def start_response(status, headers, exc_info=None):
        status_code[0] = int(status.split()[0])
        response_headers.extend(headers)

    # Call the Flask app
    result = app(environ, start_response)

    # Collect the response body
    for data in result:
        response_data.append(data)

    body = b''.join(response_data).decode('utf-8')

    # Convert headers to dict
    headers = {}
    for key, value in response_headers:
        headers[key] = value

    return {
        'statusCode': status_code[0],
        'headers': headers,
        'body': body
    }