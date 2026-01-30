touch BLOCK_B_BOT_AI/scenarios/partner_scenario.py
cat > BLOCK_B_BOT_AI/scenarios/partner_scenario.py << 'EOF'
from .base_scenario import BaseScenario

class PartnerScenario(BaseScenario):
    def process(self, user_id, message, state, metadata):
        current_step = state.get('current_step', 'start')
        
        if current_step == 'start':
            return self._handle_start(user_id, message, state)
        elif current_step == 'collect_company_name':
            return self._handle_company_name(user_id, message, state)
        else:
            return {'text': 'Начните с команды /start', 'keyboard': None}
    
    def _handle_start(self, user_id, message, state):
        state['current_step'] = 'collect_company_name'
        return {
            'text': 'Введите название вашей компании:',
            'keyboard': None
        }
    
    def _handle_company_name(self, user_id, message, state):
        self.save_to_context(state, 'company_name', message)
        return {
            'text': f'Компания "{message}" принята. Следующий шаг...',
            'keyboard': None
        }
EOF
