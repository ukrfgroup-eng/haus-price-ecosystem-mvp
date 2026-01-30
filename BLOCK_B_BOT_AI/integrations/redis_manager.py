touch BLOCK_B_BOT_AI/integrations/redis_manager.py
cat > BLOCK_B_BOT_AI/integrations/redis_manager.py << 'EOF'
import redis
import json

class RedisManager:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    def get_state(self, user_id, platform):
        key = f"bot:state:{platform}:{user_id}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return {
            'user_type': 'unknown',
            'current_step': 'start',
            'context': {}
        }
    
    def save_state(self, user_id, state, platform):
        key = f"bot:state:{platform}:{user_id}"
        self.redis.setex(key, 86400, json.dumps(state))
    
    def delete_state(self, user_id, platform):
        key = f"bot:state:{platform}:{user_id}"
        self.redis.delete(key)
EOF
