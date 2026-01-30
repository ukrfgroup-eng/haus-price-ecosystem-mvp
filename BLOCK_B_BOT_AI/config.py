touch BLOCK_B_BOT_AI/config.py
cat > BLOCK_B_BOT_AI/config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    BLOCK_A_API_URL = os.getenv('BLOCK_A_API_URL')
    BLOCK_D_API_URL = os.getenv('BLOCK_D_API_URL')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
EOF
