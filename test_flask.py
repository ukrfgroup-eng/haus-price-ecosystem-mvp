cat > test_flask.py << 'EOF'
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Flask работает!"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
EOF

python test_flask.py
