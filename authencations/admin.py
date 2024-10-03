from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .forms import CustomAdminAuthenticationForm

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'email', 'is_staff', 'is_active','is_premium',)
    list_filter = ('is_staff', 'is_active','is_premium')
    fieldsets = (
        (None, {'fields': ('phone', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active','is_premium')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('phone', 'email',)
    ordering = ('phone',)

admin.site.register(User, CustomUserAdmin)

# Tùy chỉnh trang admin để sử dụng form đăng nhập mới
admin.site.login_form = CustomAdminAuthenticationForm
admin.site.login_template = 'admin/login.html'