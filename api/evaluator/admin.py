from django.contrib import admin
from .models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_prefix', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'key_prefix')
    readonly_fields = ('key_prefix', 'key_hash', 'created_at')
    
    fieldsets = (
        ('Key Info', {
            'fields': ('name', 'is_active')
        }),
        ('Security', {
            'fields': ('key_prefix', 'key_hash'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
