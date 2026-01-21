-- SQL СХЕМА БАЗЫ ДАННЫХ ДЛЯ ПАРТНЕРОВ
-- Блок A: База партнеров + верификация

-- Таблица партнеров
CREATE TABLE IF NOT EXISTS partners (
    id SERIAL PRIMARY KEY,
    partner_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Юридические данные
    company_name VARCHAR(200) NOT NULL,
    legal_form VARCHAR(20) NOT NULL,
    inn VARCHAR(12) UNIQUE NOT NULL,
    ogrn VARCHAR(15),
    kpp VARCHAR(9),
    legal_address TEXT,
    actual_address TEXT,
    registration_date DATE,
    
    -- Контактные данные
    contact_person VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL,
    website VARCHAR(200),
    telegram VARCHAR(50),
    whatsapp VARCHAR(20),
    
    -- Профиль услуг
    main_category VARCHAR(50) NOT NULL,
    specializations JSONB DEFAULT '[]',
    services JSONB DEFAULT '[]',
    
    -- География
    regions JSONB DEFAULT '[]',
    cities JSONB DEFAULT '[]',
    radius_km INTEGER DEFAULT 50,
    
    -- Верификация
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    verification_date TIMESTAMP,
    verified_by VARCHAR(50),
    documents JSONB DEFAULT '[]',
    rejection_reason TEXT,
    
    -- Статус и настройки
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    subscription_type VARCHAR(20) NOT NULL DEFAULT 'free',
    subscription_expires TIMESTAMP,
    max_active_leads INTEGER DEFAULT 3,
    
    -- Рейтинг и статистика
    rating FLOAT DEFAULT 0.0,
    completed_projects INTEGER DEFAULT 0,
    response_rate FLOAT DEFAULT 0.0,
    
    -- Технические поля
    settings JSONB DEFAULT '{}',
    
    -- Индексы для быстрого поиска
    CONSTRAINT check_rating_range CHECK (rating >= 0 AND rating <= 5),
    CONSTRAINT check_response_rate CHECK (response_rate >= 0 AND response_rate <= 100)
);

-- Индексы для таблицы partners
CREATE INDEX idx_partners_verification_status ON partners(verification_status);
CREATE INDEX idx_partners_is_active ON partners(is_active);
CREATE INDEX idx_partners_regions ON partners USING GIN(regions);
CREATE INDEX idx_partners_specializations ON partners USING GIN(specializations);
CREATE INDEX idx_partners_rating ON partners(rating DESC);
CREATE INDEX idx_partners_created_at ON partners(created_at DESC);

-- Таблица логов верификации
CREATE TABLE IF NOT EXISTS partner_verification_logs (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    partner_code VARCHAR(50) NOT NULL,
    
    -- Детали действия
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB,
    
    -- Кто выполнил
    performed_by VARCHAR(50),
    performed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Индексы
    INDEX idx_verification_logs_partner_id (partner_id),
    INDEX idx_verification_logs_performed_at (performed_at DESC)
);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER update_partners_updated_at BEFORE UPDATE
ON partners FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Представление для быстрого доступа к верифицированным партнерам
CREATE OR REPLACE VIEW verified_partners AS
SELECT 
    p.partner_code,
    p.company_name,
    p.legal_form,
    p.inn,
    p.contact_person,
    p.phone,
    p.email,
    p.main_category,
    p.specializations,
    p.services,
    p.regions,
    p.cities,
    p.rating,
    p.completed_projects,
    p.response_rate,
    p.subscription_type
FROM partners p
WHERE p.verification_status = 'verified' 
  AND p.is_active = TRUE
  AND (p.subscription_expires IS NULL OR p.subscription_expires > NOW());

-- Статистика партнеров
CREATE OR REPLACE VIEW partners_statistics AS
SELECT 
    COUNT(*) as total_partners,
    COUNT(CASE WHEN verification_status = 'verified' THEN 1 END) as verified_partners,
    COUNT(CASE WHEN verification_status = 'pending' THEN 1 END) as pending_partners,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_partners,
    AVG(rating) as average_rating,
    SUM(completed_projects) as total_projects
FROM partners;

-- Комментарии к таблицам
COMMENT ON TABLE partners IS 'Таблица партнеров (строительных компаний)';
COMMENT ON COLUMN partners.partner_code IS 'Уникальный код партнера в системе';
COMMENT ON COLUMN partners.verification_status IS 'Статус верификации: pending, verified, rejected';
COMMENT ON COLUMN partners.subscription_type IS 'Тип подписки: free, basic, premium';

COMMENT ON TABLE partner_verification_logs IS 'Логи верификации партнеров';
COMMENT ON COLUMN partner_verification_logs.action IS 'Тип действия: inn_check, document_upload, manual_review';
COMMENT ON COLUMN partner_verification_logs.status IS 'Результат: success, failed, pending';
