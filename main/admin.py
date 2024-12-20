from django.contrib import admin
from .models import TablaCorrespondencias, Texto


@admin.register(TablaCorrespondencias)
class TablaCorrespondenciasAdmin(admin.ModelAdmin):
    list_display = ('lexema', 'token', 'ponderacion')
    list_filter = ('token',)
    search_fields = ('lexema',)
    ordering = ('lexema',)

admin.site.register(Texto)