from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/check', methods=['POST'])
def check_inn():
    data = request.json
    inn = data.get('inn', '')
    # Всегда возвращаем успех для тестов
    return jsonify({
        "valid": True,
        "company_name": "ООО Тестовая Компания",
        "status": "ACTIVE"
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "fns-mock"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9003, debug=True)
