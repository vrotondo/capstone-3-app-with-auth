from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello! Flask is working on Windows!"

@app.route('/test')
def test():
    return "Test endpoint working!"

if __name__ == '__main__':
    print("Starting test server...")
    print("Open http://localhost:8000 in your browser")
    app.run(debug=True, port=8000, host='127.0.0.1')