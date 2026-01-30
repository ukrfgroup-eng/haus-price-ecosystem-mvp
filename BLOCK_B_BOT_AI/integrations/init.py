mkdir -p BLOCK_B_BOT_AI/integrations
touch BLOCK_B_BOT_AI/integrations/__init__.py
cat > BLOCK_B_BOT_AI/integrations/__init__.py << 'EOF'
from .redis_manager import RedisManager
from .api_client import APIClient
EOF
