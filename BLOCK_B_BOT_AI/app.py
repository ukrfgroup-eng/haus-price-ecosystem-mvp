touch BLOCK_B_BOT_AI/app.py
cat > BLOCK_B_BOT_AI/app.py << 'EOF'
from flask import Flask, request, jsonify
from bot_core import BotCore
from integrations.redis_manager import RedisManager

app = Flask(__name__)

redis_manager = RedisManager('redis://localhost:6379/0')
bot = BotCore(redis_manager)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/v1/bot/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({'error': 'Invalid data'}), 400
    
    response = bot.process_message(user_id, message, 'telegram', data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
EOF
