from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World! Flask server is running!'

@app.route('/test')
def test():
    return 'Test endpoint is working!'

if __name__ == '__main__':
    print("Starting test server on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000) 