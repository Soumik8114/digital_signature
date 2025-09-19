from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UploadedFile,UserKeyPair
from .utils import create_or_update_user_keys

class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner', 'upload_date','signature')
    fields = ('uploaded_file', 'owner', 'upload_date','signature')

    def delete_model(self, request, obj):
        obj.uploaded_file.delete(save=False)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.uploaded_file.delete(save=False)
        super().delete_queryset(request, queryset)

class CustomUserAdmin(BaseUserAdmin):
    actions = ['regenerate_key_pairs']

    @admin.action(description='Regenerate key pairs for selected users')
    def regenerate_key_pairs(self, request, queryset):
        """
        Admin action to regenerate key pairs for selected users.
        """
        count = 0
        for user in queryset:
            create_or_update_user_keys(user)
            count += 1
        
        self.message_user(request, f'{count} user(s) had their key pairs successfully regenerated.', messages.SUCCESS)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UploadedFile, UploadedFileAdmin)
admin.site.register(UserKeyPair)