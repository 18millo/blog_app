from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Author, Blog, Subscriber

admin.site.register(Author)
admin.site.register(Blog)
admin.site.register(Subscriber)
admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_count']
    search_fields = ['name']
    filter_horizontal = ['permissions']

    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Users'
