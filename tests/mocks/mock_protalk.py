from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"[Protalk Mock] Received: {data}")
    return jsonify({"received": True, "data": data})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "protalk-mock"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
