from django.db import models
import secrets
import hashlib


class ApiKey(models.Model):
    name = models.CharField(max_length=100, unique=True)
    key_prefix = models.CharField(max_length=10)  # First 10 chars visible
    key_hash = models.CharField(max_length=255, unique=True)  # SHA-256 hash
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
    
    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"
    
    @staticmethod
    def generate_key():
        """Generate a new random API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_key(key):
        """Hash an API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @classmethod
    def create_key(cls, name):
        """Create and save a new API key, return the full key once"""
        full_key = cls.generate_key()
        key_hash = cls.hash_key(full_key)
        key_prefix = full_key[:10]
        
        api_key_obj = cls.objects.create(
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash
        )
        
        return full_key, api_key_obj
    
    @classmethod
    def verify_key(cls, provided_key):
        """Verify if a provided key matches a stored hash"""
        key_hash = cls.hash_key(provided_key)
        try:
            return cls.objects.get(key_hash=key_hash, is_active=True)
        except cls.DoesNotExist:
            return None
