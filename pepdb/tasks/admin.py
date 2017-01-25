from django.contrib import admin
from tasks.models import PersonDeduplication


# Register your models here.
class PersonDeduplicationAdmin(admin.ModelAdmin):
    list_display = ("person1", "person2", "timestamp")
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False


admin.site.register(PersonDeduplication, PersonDeduplicationAdmin)
