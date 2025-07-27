from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.utils.safestring import mark_safe
import json
from django.db.models.functions import TruncMonth
import calendar
from .models import Stok, Tarif, TarifMalzemesi, Menu, Siparis, SiparisOgeleri, Bildirim, GelirGider, Kullanici,Kategori,Masa


@admin.register(Kullanici)
class CustomUserAdmin(UserAdmin):
    model = Kullanici
    list_display = ['username', 'email', 'rol', 'is_staff', 'is_active']
    list_filter = ['rol', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('rol',)}),
    )
    search_fields = ['username', 'email']
    ordering = ['username']
    


class MenuAdmin(admin.ModelAdmin):
    list_display = ('yemek_adi', 'kategori', 'fiyat')
    list_filter = ('kategori',)  # Bu sayede sağda kategori filtresi görünür

admin.site.register(Menu, MenuAdmin)

@admin.register(Stok)
class StokAdmin(admin.ModelAdmin):
    list_display = ('malzeme_adi', 'miktar', 'birim', 'birim_fiyat', 'toplam_maliyet')

class GelirGiderAdmin(admin.ModelAdmin):
    change_list_template = 'restaurant/gelir_raporu.html'  # Grafikli özel şablon

    def changelist_view(self, request, extra_context=None):
        # Aylık gelir ve gider verileri
        queryset = self.model.objects.all()

        ay_gelir = queryset.filter(tur='gelir').annotate(
            ay=TruncMonth('tarih')
        ).values('ay').annotate(toplam=Sum('tutar')).order_by('ay')

        ay_gider = queryset.filter(tur='gider').annotate(
            ay=TruncMonth('tarih')
        ).values('ay').annotate(toplam=Sum('tutar')).order_by('ay')

        def ay_label(veri):
            return [calendar.month_name[v['ay'].month] for v in veri]

        def ay_deger(veri):
            return [float(v['toplam']) for v in veri]

        aylar = ay_label(ay_gelir)
        gelirler = ay_deger(ay_gelir)
        giderler = ay_deger(ay_gider)

        toplam_gelir = queryset.filter(tur='gelir').aggregate(Sum('tutar'))['tutar__sum'] or 0
        toplam_gider = queryset.filter(tur='gider').aggregate(Sum('tutar'))['tutar__sum'] or 0
        bakiye = toplam_gelir - toplam_gider

        extra_context = extra_context or {}
        extra_context.update({
            'aylar': aylar,
            'gelirler': gelirler,
            'giderler': giderler,
            'toplam_gelir': toplam_gelir,
            'toplam_gider': toplam_gider,
            'bakiye': bakiye,
        })

        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(GelirGider, GelirGiderAdmin)

admin.site.site_header = "Restoran Otomasyonu Yönetimi"
admin.site.site_title = "Restoran Admin"
admin.site.index_title = "Yönetim Paneline Hoş Geldiniz"








admin.site.register(Tarif)
admin.site.register(TarifMalzemesi)
admin.site.register(Siparis)
admin.site.register(SiparisOgeleri)
admin.site.register(Bildirim)
admin.site.register(Kategori)
admin.site.register(Masa)
