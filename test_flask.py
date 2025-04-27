from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Flask Test</title>
        </head>
        <body>
            <h1>Flask Test Page</h1>
            <p>If you see this, your browser can connect to the server!</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5000")
    print("Press Ctrl+C to quit")
    app.run(host='0.0.0.0', port=5000, debug=True) 