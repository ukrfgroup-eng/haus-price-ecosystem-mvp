from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/pay', methods=['POST'])
def pay():
    return jsonify({"success": True, "payment_id": "test_123"})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "payment-mock"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9004, debug=True)
