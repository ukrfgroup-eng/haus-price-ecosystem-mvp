"""
Интеграция с S3-хранилищем для документов партнеров
Поддерживает AWS S3, MinIO и другие S3-совместимые хранилища
"""

import boto3
import logging
from typing import Optional, Dict, Any, BinaryIO
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class S3Storage:
    """Клиент для работы с S3 хранилищем"""
    
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        bucket_name: str = "haus-partners-documents",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: str = "us-east-1",
        use_ssl: bool = True
    ):
        """
        Инициализация S3 клиента
        
        Args:
            endpoint_url: URL S3-совместимого хранилища (None для AWS S3)
            bucket_name: Имя бакета
            access_key: Access key ID
            secret_key: Secret access key
            region: Регион
            use_ssl: Использовать SSL
        """
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        
        # Конфигурация клиента
        client_config = {
            'region_name': region,
            'use_ssl': use_ssl
        }
        
        if endpoint_url:
            client_config['endpoint_url'] = endpoint_url
        
        # Создаем клиента
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            **client_config
        )
        
        # Проверяем доступность бакета
        self._ensure_bucket_exists()
    
    def upload_document(
        self,
        partner_id: str,
        document_type: str,
        file_content: bytes,
        filename: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Загрузка документа в S3
        
        Args:
            partner_id: ID партнера
            document_type: Тип документа (inn, passport, license и т.д.)
            file_content: Содержимое файла в виде bytes
            filename: Оригинальное имя файла
            metadata: Дополнительные метаданные
            
        Returns:
            Информация о загруженном файле
        """
        try:
            # Генерация пути в S3
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(filename)
            s3_key = f"partners/{partner_id}/{document_type}/{timestamp}_{safe_filename}"
            
            # Базовые метаданные
            file_metadata = {
                'partner_id': partner_id,
                'document_type': document_type,
                'original_filename': filename,
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
            # Добавляем пользовательские метаданные
            if metadata:
                file_metadata.update(metadata)
            
            # Определяем Content-Type
            content_type = self._detect_content_type(filename)
            
            # Загружаем файл
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=file_metadata,
                ACL='private'  # Файлы приватные по умолчанию
            )
            
            # Генерируем пресайнд URL для временного доступа
            presigned_url = self.generate_presigned_url(s3_key, expires_in=3600)
            
            return {
                'success': True,
                's3_key': s3_key,
                'bucket': self.bucket_name,
                'filename': filename,
                'content_type': content_type,
                'size_bytes': len(file_content),
                'presigned_url': presigned_url,
                'metadata': file_metadata
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e.response['Error']['Message']}")
            return {
                'success': False,
                'error': e.response['Error']['Message'],
                'code': e.response['Error']['Code']
            }
        except Exception as e:
            logger.error(f"Unexpected S3 upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_document(self, s3_key: str) -> Optional[bytes]:
        """
        Скачивание документа из S3
        
        Args:
            s3_key: Ключ файла в S3
            
        Returns:
            Содержимое файла или None при ошибке
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response['Body'].read()
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Document not found: {s3_key}")
            else:
                logger.error(f"S3 download error: {e.response['Error']['Message']}")
            return None
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        expires_in: int = 3600,
        download_filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Генерация временной ссылки для доступа к файлу
        
        Args:
            s3_key: Ключ файла в S3
            expires_in: Время жизни ссылки в секундах
            download_filename: Имя файла для скачивания (опционально)
            
        Returns:
            Пресайнд URL или None при ошибке
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': s3_key
            }
            
            # Добавляем параметр для скачивания с определенным именем
            if download_filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{download_filename}"'
            
            url = self.client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expires_in
            )
            
            return url
            
        except ClientError as e:
            logger.error(f"S3 presigned URL error: {e.response['Error']['Message']}")
            return None
    
    def delete_document(self, s3_key: str) -> bool:
        """
        Удаление документа из S3
        
        Args:
            s3_key: Ключ файла в S3
            
        Returns:
            Успешность удаления
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Document deleted: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 delete error: {e.response['Error']['Message']}")
            return False
    
    def list_partner_documents(self, partner_id: str) -> Dict[str, Any]:
        """
        Получение списка документов партнера
        
        Args:
            partner_id: ID партнера
            
        Returns:
            Список документов
        """
        try:
            prefix = f"partners/{partner_id}/"
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            documents = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Получаем метаданные для каждого объекта
                    metadata = self.get_object_metadata(obj['Key'])
                    
                    documents.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'metadata': metadata
                    })
            
            return {
                'success': True,
                'partner_id': partner_id,
                'documents': documents,
                'count': len(documents)
            }
            
        except ClientError as e:
            logger.error(f"S3 list error: {e.response['Error']['Message']}")
            return {
                'success': False,
                'error': e.response['Error']['Message'],
                'documents': []
            }
    
    def get_object_metadata(self, s3_key: str) -> Dict[str, str]:
        """
        Получение метаданных объекта
        
        Args:
            s3_key: Ключ файла в S3
            
        Returns:
            Метаданные объекта
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response.get('Metadata', {})
            
        except ClientError:
            return {}
    
    def copy_document(self, source_key: str, destination_key: str) -> bool:
        """
        Копирование документа в S3
        
        Args:
            source_key: Исходный ключ
            destination_key: Ключ назначения
            
        Returns:
            Успешность копирования
        """
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }
            
            self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource=copy_source,
                Key=destination_key
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"S3 copy error: {e.response['Error']['Message']}")
            return False
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """
        Получение статистики использования хранилища
        
        Returns:
            Статистика хранилища
        """
        try:
            total_size = 0
            total_files = 0
            
            paginator = self.client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket_name):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj['Size']
                        total_files += 1
            
            return {
                'success': True,
                'bucket': self.bucket_name,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'total_files': total_files,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"S3 storage usage error: {e.response['Error']['Message']}")
            return {
                'success': False,
                'error': e.response['Error']['Message']
            }
    
    def _ensure_bucket_exists(self):
        """Проверка существования бакета, создание при необходимости"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket exists: {self.bucket_name}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                # Бакет не существует, создаем
                try:
                    logger.info(f"Creating bucket: {self.bucket_name}")
                    
                    create_kwargs = {
                        'Bucket': self.bucket_name,
                        'ACL': 'private'
                    }
                    
                    # Для S3-совместимых хранилищ может потребоваться специальная конфигурация
                    if self.endpoint_url and 'minio' in self.endpoint_url:
                        # MinIO специфичные настройки
                        create_kwargs['CreateBucketConfiguration'] = {
                            'LocationConstraint': ''
                        }
                    
                    self.client.create_bucket(**create_kwargs)
                    
                    # Настраиваем политики безопасности
                    self._configure_bucket_policies()
                    
                    logger.info(f"Bucket created: {self.bucket_name}")
                    
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                # Другая ошибка
                logger.error(f"Error checking bucket: {error_code}")
                raise
    
    def _configure_bucket_policies(self):
        """Настройка политик безопасности бакета"""
        try:
            # Блокируем публичный доступ
            self.client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            # Настраиваем жизненный цикл для старых документов
            lifecycle_configuration = {
                'Rules': [
                    {
                        'ID': 'DeleteOldDocuments',
                        'Status': 'Enabled',
                        'Filter': {
                            'Prefix': 'partners/'
                        },
                        'Expiration': {
                            'Days': 365 * 5  # Удаляем через 5 лет
                        }
                    }
                ]
            }
            
            self.client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration=lifecycle_configuration
            )
            
        except ClientError as e:
            logger.warning(f"Could not configure bucket policies: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Очистка имени файла от небезопасных символов
        
        Args:
            filename: Исходное имя файла
            
        Returns:
            Безопасное имя файла
        """
        import re
        import unicodedata
        
        # Нормализуем Unicode
        filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
        
        # Убираем небезопасные символы
        filename = re.sub(r'[^\w\s\-\.]', '_', filename)
        
        # Убираем лишние пробелы и подчеркивания
        filename = re.sub(r'[\s_]+', '_', filename)
        
        # Обрезаем длину
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            name = name[:95]
            filename = f"{name}.{ext}" if ext else name
        
        return filename
    
    def _detect_content_type(self, filename: str) -> str:
        """
        Определение Content-Type по расширению файла
        
        Args:
            filename: Имя файла
            
        Returns:
            MIME-тип
        """
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'tiff': 'image/tiff',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'txt': 'text/plain',
            'csv': 'text/csv'
        }
        
        return mime_types.get(extension, 'application/octet-stream')
