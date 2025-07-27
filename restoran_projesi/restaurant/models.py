from django.db import models
from django.contrib.auth.models import AbstractUser

#KULLANICI MODELİ 
class Kullanici(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Admin'),
        ('sef', 'Şef'),
        ('garson', 'Garson'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='garson')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

#STOK MODELİ
class Stok(models.Model):
    BIRIMLER = (
        ('gr', 'Gram'),
        ('kg', 'Kilogram'),
        ('adet', 'Adet'),
        ('litre', 'Litre'),
    )
    malzeme_adi = models.CharField(max_length=100)
    birim = models.CharField(max_length=10, choices=BIRIMLER)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.malzeme_adi} ({self.miktar} {self.birim})"
    @property
    def toplam_maliyet(self):
        return self.miktar * self.birim_fiyat
    toplam_maliyet.fget.short_description = 'Toplam Maliyet' 

    class Meta:
        verbose_name = "Stok Malzemesi"
        verbose_name_plural = "Stok Malzemeleri"

#Kategori Modeli 
class Kategori(models.Model):
    ad = models.CharField(max_length=100)

    def __str__(self):
        return self.ad
class Kategori(models.Model):
    ad = models.CharField(max_length=100)

    def __str__(self):
        return self.ad
    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'

#TARİF MODELİ
class Tarif(models.Model):
    tarif_adi = models.CharField(max_length=100)
    aciklama = models.TextField(blank=True)

    def __str__(self):
        return self.tarif_adi

    class Meta:
        verbose_name = "Tarif"
        verbose_name_plural = "Tarifler"

#TARİF MALZEMESİ MODELİ
class TarifMalzemesi(models.Model):
    tarif = models.ForeignKey(Tarif, on_delete=models.CASCADE)
    stok = models.ForeignKey(Stok, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    
    BIRIM_CHOICES = [
        ('gr', 'Gram'),
        ('kg', 'Kilogram'),
        ('litre', 'Litre'),
        ('adet', 'Adet'),
    ]
    birim = models.CharField(max_length=10, choices=BIRIM_CHOICES)

    def __str__(self):
        return f"{self.tarif.tarif_adi} - {self.stok.malzeme_adi}"

    class Meta:
        verbose_name = "Tarif Malzemesi"
        verbose_name_plural = "Tarif Malzemeleri"

#MENÜ MODELİ
class Menu(models.Model):
    KATEGORI_CHOICES = [
        ('baslangic', 'Başlangıç'),
        ('anayemek', 'Ana Yemek'),
        ('tatli', 'Tatlı'),
        ('salata', 'Salata'),
        ('icecek', 'İçecek'),
    ]
    yemek_adi = models.CharField(max_length=100)
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    tarif = models.ForeignKey(Tarif, null=True, blank=True, on_delete=models.SET_NULL)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='yemek')

    def __str__(self):
        return self.yemek_adi

    class Meta:
        verbose_name = "Menü"
        verbose_name_plural = "Menüler"


#MASA MODELİ
class Masa(models.Model):
    numara = models.PositiveIntegerField(unique=True)
    DOLULUK_DURUMU = (
        ('bos', 'Boş'),
        ('dolu', 'Dolu'),
    )
    durum = models.CharField(max_length=10, choices=DOLULUK_DURUMU, default='bos')

    def __str__(self):
        return f"Masa {self.numara} - {self.get_durum_display()}"
    class Meta:
        verbose_name = "Masa"
        verbose_name_plural = "Masalar"


#SİPARİŞ MODELİ
class Siparis(models.Model):
    DURUMLAR = (
        ('bekliyor', 'Bekliyor'),
        ('hazırlanıyor', 'Hazırlanıyor'),
        ('hazır', 'Hazır'),
        ('stok_yetersiz', 'Stok Yetersiz '),
        ('teslim_edildi', 'Teslim Edildi'), 
        ('stok_yetersiz', 'Stok Yetersiz'),
        ('iptal_edildi', 'İptal Edildi'),
    )
    masa = models.ForeignKey(Masa, on_delete=models.SET_NULL, null=True, blank=True, related_name='siparisler_masa') 
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2)
    durum = models.CharField(max_length=20, choices=DURUMLAR, default='bekliyor')
    tarih_saat = models.DateTimeField(auto_now_add=True)
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    odendi = models.BooleanField(default=False)
    kullanici = models.ForeignKey(Kullanici, on_delete=models.SET_NULL, null=True, blank=True, related_name='siparisler_kullanici')

    def __str__(self):
        masa_str = f"Masa {self.masa.numara}" if self.masa else "Masa Yok"
        return f"{masa_str} - {self.get_durum_display()}"

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"

#SİPARİŞ ÖĞELERİ MODELİ
class SiparisOgeleri(models.Model):
    siparis = models.ForeignKey(Siparis, on_delete=models.CASCADE, related_name='ogeler')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    adet = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.adet}x {self.menu.yemek_adi} (Sipariş: {self.siparis.id})"
    
    @property
    def toplam_fiyat(self):
        return self.adet * self.menu.fiyat

    class Meta:
        verbose_name = "Sipariş Öğesi"
        verbose_name_plural = "Sipariş Öğeleri"

#BİLDİRİM MODELİ
class Bildirim(models.Model):
    DURUMLAR = (
        ('okunmadı', 'Okunmadı'),
        ('okundu', 'Okundu'),
    )
    kullanici = models.ForeignKey(Kullanici, on_delete=models.CASCADE)
    mesaj = models.TextField()
    durum = models.CharField(max_length=10, choices=DURUMLAR, default='okunmadı')
    tarih_saat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kullanici} - {self.durum}"

    class Meta:
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"

#GELİR-GİDER MODELİ
class GelirGider(models.Model):
    TUR = (
        ('gelir', 'Gelir'),
        ('gider', 'Gider'),
    )
    tur = models.CharField(max_length=10, choices=TUR)
    tutar = models.DecimalField(max_digits=10, decimal_places=2)
    aciklama = models.TextField(blank=True)
    tarih = models.DateField()

    def __str__(self):
        return f"{self.tur} - {self.tutar} TL"

    class Meta:
        verbose_name = "Gelir"
        verbose_name_plural = "Gelir Kayıtları"




