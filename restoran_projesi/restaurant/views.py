from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from .models import Menu, Siparis, SiparisOgeleri, Stok,Tarif, TarifMalzemesi, GelirGider, Masa, Bildirim, GelirGider
from collections import defaultdict
from django.http import HttpResponseForbidden
from .decorators import role_required
from django.contrib.auth.models import Group
from datetime import date, timedelta
import json
from django.utils import timezone
from django.db.models import Sum
from django.db import models
from django.db.models.functions import TruncDate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import TruncMonth, TruncDay
import calendar
from . import views






@login_required
def admin_panel(request):
    return HttpResponse("Admin paneli yok ama bu fonksiyon eklendi, hata çözüldü.")

def index(request):
    return render(request, 'restaurant/index.html')
    

def menu_listesi(request):
    menuler = Menu.objects.all()
    return render(request, 'restaurant/menu_listesi.html', {'menuler': menuler})

@login_required
@role_required('garson') 
def siparis_olustur(request):
    menuler = Menu.objects.all()
    masalar = Masa.objects.all()  

    if request.method == 'POST':
        masa_no = request.POST.get('masa_no')
        yemek_id = request.POST.getlist('yemek_id')
        adetler = request.POST.getlist('adet')

        if not masa_no:
            messages.error(request, "Lütfen bir masa seçin.")
            return render(request, 'restaurant/siparis_olustur.html', {
                'menuler': menuler,
                'masalar': masalar
            })

        toplam_tutar = 0
        siparis = Siparis.objects.create(
            masa_no=masa_no,
            toplam_tutar=0,
            kullanici=request.user  
        )

        for i in range(len(yemek_id)):
            menu = Menu.objects.get(id=yemek_id[i])
            adet = int(adetler[i])
            SiparisOgeleri.objects.create(
                siparis=siparis,
                menu=menu,
                adet=adet
            )
            toplam_tutar += adet * float(menu.fiyat)

        siparis.toplam_tutar = toplam_tutar
        siparis.save()

        return redirect('siparis_basari')

    return render(request, 'restaurant/siparis_olustur.html', {
        'menuler': menuler,
        'masalar': masalar
    })


def siparis_basari(request):
    return render(request, 'restaurant/siparis_basari.html')

@login_required
def siparislerim(request):
    kullanici = request.user
    if kullanici.rol != 'garson':
        return redirect('login')

    # Garsonun henüz ödemesi yapılmamış siparişleri
    siparisler = Siparis.objects.filter(kullanici=kullanici, odendi=False).order_by('-tarih_saat')

    context = {
        'siparisler': siparisler,
    }
    return render(request, 'restaurant/siparislerim.html', context)


@role_required(['sef'])
def sef_panel(request):
    # Bekleyen siparişleri getir
    siparisler = Siparis.objects.filter(durum__in=['bekliyor', 'hazırlanıyor']).prefetch_related(
    'ogeler__menu__tarif__tarifmalzemesi_set__stok'
).order_by('-tarih_saat')
    
    tarifler = Tarif.objects.all().prefetch_related('tarifmalzemesi_set__stok')
    stoklar = Stok.objects.all()

    context = {
        'siparisler': siparisler,
        'tarifler': tarifler,
        'stoklar': stoklar,
    }
    return render(request, 'restaurant/sef_panel.html', context)

@login_required
@role_required(['sef'])
def siparis_durum_guncelle(request, siparis_id):
    siparis = get_object_or_404(Siparis, id=siparis_id)

    if request.method == "POST":
        yeni_durum = request.POST.get('durum')
        if yeni_durum in dict(Siparis.DURUMLAR).keys():
            siparis.durum = yeni_durum
            siparis.save()

            # Eğer sipariş hazırlandıysa bekleyenler listesinden kalkması için:
            if yeni_durum == 'hazır':
                messages.success(request, f"Sipariş {siparis.id} hazırlandı ve bekleyenlerden kaldırıldı.")
            else:
                messages.success(request, f"Sipariş durumu '{siparis.get_durum_display()}' olarak güncellendi.")

    return redirect('sef_panel')

def debug_menuler():
    yemekler = Menu.objects.all()
    for y in yemekler:
        print(f"Yemek: {y.yemek_adi}, Kategori: {y.kategori}, Görünüm: {y.get_kategori_display()}")

@login_required
def tarif_ekle(request):
    stoklar = Stok.objects.all()

    if request.method == 'POST':
        tarif_adi = request.POST.get('tarif_adi') or request.POST.get('ad')
        aciklama = request.POST.get('aciklama')
        malzemeler = request.POST.getlist('malzeme')
        miktarlar = request.POST.getlist('miktar')
        birimler = request.POST.getlist('birim')

        if not tarif_adi or not aciklama or not malzemeler:
            messages.error(request, "Tüm alanları doldurmanız gerekir.")
            return redirect('tarif_ekle')

        tarif = Tarif.objects.create(tarif_adi=tarif_adi, aciklama=aciklama)

        for malzeme_id, miktar, birim in zip(malzemeler, miktarlar, birimler):
            if malzeme_id and miktar and birim:
                TarifMalzemesi.objects.create(
                    tarif=tarif,
                    stok_id=malzeme_id,
                    miktar=float(miktar),
                    birim=birim
                )

        messages.success(request, "Tarif başarıyla eklendi.")
        return redirect('tarif_ekle')

    return render(request, 'restaurant/tarif_ekle.html', {'stoklar': stoklar})

@login_required
@role_required('garson')
def garson_panel(request):
    kullanici = request.user
    if kullanici.rol != 'garson':
        return redirect('login')  # Yetkisiz kullanıcı için

    masalar = Masa.objects.all().order_by('numara')
    menuler = Menu.objects.all().order_by('kategori', 'yemek_adi')

    secilen_masa_id = request.GET.get('masa_id')
    secilen_masa = None
    siparisler = None

    if secilen_masa_id:
        secilen_masa = get_object_or_404(Masa, id=secilen_masa_id)
        # Bu masaya ait aktif siparişleri getirmesi için (ödeme yapılmamış, iptal edilmemiş)
        siparisler = Siparis.objects.filter(masa=secilen_masa, odendi=False).order_by('-tarih_saat')

    if request.method == 'POST':
        masa_id = request.POST.get('masa_id')
        menu_id = request.POST.get('menu_id')
        adet = request.POST.get('adet')

        if masa_id and menu_id and adet:
            try:
                adet = int(adet)
                if adet < 1:
                    raise ValueError
            except ValueError:
                adet = 1  

            masa = get_object_or_404(Masa, id=masa_id)
            menu = get_object_or_404(Menu, id=menu_id)

            # Var olan siparişi al ya da yeni sipariş oluştur
            siparis, created = Siparis.objects.get_or_create(
                masa=masa, odendi=False, durum='bekliyor', kullanici=kullanici,
                defaults={'toplam_tutar': 0}
            )
            # Sipariş öğesi oluştur veya adet güncelle
            siparis_ogesi, og_created = SiparisOgeleri.objects.get_or_create(
                siparis=siparis,
                menu=menu,
                defaults={'adet': adet}
            )
            if not og_created:
                siparis_ogesi.adet += adet
                siparis_ogesi.save()

            # Toplam tutarı güncelle
            toplam = SiparisOgeleri.objects.filter(siparis=siparis).aggregate(
                toplam=Sum(models.F('adet') * models.F('menu__fiyat'))
            )['toplam'] or 0
            siparis.toplam_tutar = toplam
            siparis.save()

            # Masa durumunu dolu yap
            masa.durum = 'dolu'
            masa.save()

            return redirect(f'/garson-panel/?masa_id={masa.id}')  # tekrar aynı sayfaya yönlendir

    context = {
        'masalar': masalar,
        'menuler': menuler,
        'secilen_masa': secilen_masa,
        'siparisler': siparisler,
    }
    return render(request, 'restaurant/garson_panel.html', context)


@login_required
def masa_siparis_al(request, masa_id):
    masa = get_object_or_404(Masa, id=masa_id)
    menuler = Menu.objects.all().order_by('kategori', 'yemek_adi')
    kategoriler = Menu.objects.values_list('kategori', flat=True).distinct() # Menüdeki tüm kategorileri çekiyoruz

    # Eğer masa doluysa ve aktif bir sipariş varsa, mevcut siparişi getirelim
    aktif_siparis = None
    if masa.durum == 'dolu':
        # Ödenmemiş ve iptal edilmemiş siparişleri ara
        aktif_siparis = Siparis.objects.filter(
            masa=masa,
            odendi=False,
            durum__in=['bekliyor', 'hazirlaniyor', 'hazir', 'stok_yetersiz'] # Sadece aktif durumdaki siparişler
        ).order_by('-tarih_saat').first() # En sonuncuyu alıyoruz

    if request.method == 'POST':
        # Yeni sipariş oluşturma veya mevcut siparişi güncelleme
        yemek_secimleri = json.loads(request.POST.get('yemek_secimleri', '[]'))

        if not yemek_secimleri:
            messages.error(request, "Lütfen sipariş için en az bir ürün seçin.")
            return redirect('masa_siparis_al', masa_id=masa.id)

        try:
            with transaction.atomic():
                if aktif_siparis:
                    # Mevcut siparişe yeni ürünler ekle
                    siparis = aktif_siparis
                    messages.info(request, f"Masa {masa.numara} için mevcut sipariş güncelleniyor.")
                else:
                    # Yeni sipariş oluştur
                    siparis = Siparis.objects.create(
                        masa=masa,
                        kullanici=request.user,
                        durum='bekliyor',
                        toplam_tutar=Decimal('0.00') # Başlangıçta 0 olarak set et
                    )
                    messages.success(request, f"Masa {masa.numara} için yeni sipariş oluşturuldu.")

                # Sipariş kalemlerini işle
                anlik_toplam_tutar = Decimal('0.00')
                for item in yemek_secimleri:
                    yemek_id = item['id']
                    adet = int(item['adet'])
                    menu_urun = get_object_or_404(Menu, id=yemek_id)

                    # Mevcut sipariş öğesini bul veya oluştur
                    siparis_ogesi, created = SiparisOgeleri.objects.get_or_create(
                        siparis=siparis,
                        menu=menu_urun,
                        defaults={'adet': adet}
                    )
                    if not created:
                        # Eğer öğe zaten varsa, adetini güncelle (üstüne ekle)
                        siparis_ogesi.adet += adet
                        siparis_ogesi.save()

                    anlik_toplam_tutar += menu_urun.fiyat * adet

                # her defasında tüm sipariş öğelerinin toplamını yeniden hesaplayalım.
                siparis.toplam_tutar = sum(item.toplam_fiyat for item in siparis.ogeler.all())
                siparis.save()


                # Masa durumunu dolu yap
                masa.durum = 'dolu'
                masa.save()

                # Şef paneline bildirim gönder 
                Bildirim.objects.create(
                    kullanici=request.user, # Bildirimi oluşturan garson
                    mesaj=f"Masa {masa.numara} için yeni sipariş alındı! Sipariş ID: {siparis.id}",
                    durum='okunmadi'
                )

                messages.success(request, "Sipariş başarıyla alındı ve şefe iletildi.")
                return redirect('garson_panel')

        except Exception as e:
            messages.error(request, f"Sipariş alınırken bir hata oluştu: {e}")
            # Hata durumunda formu tekrar yükle
            return render(request, 'restaurant/masa_detay.html', {
                'masa': masa,
                'menuler': menuler,
                'kategoriler': kategoriler,
                'aktif_siparis': aktif_siparis,
            })

    # GET isteği
    context = {
        'masa': masa,
        'menuler': menuler,
        'kategoriler': kategoriler,
        'aktif_siparis': aktif_siparis, # Sayfaya mevcut sipariş bilgisini gönder
    }
    return render(request, 'restaurant/masa_detay.html', context)

@login_required
@role_required('garson')
def garson_siparislerim(request):
    siparisler = Siparis.objects.filter(garson=request.user).order_by('-tarih_saat')
    return render(request, 'garson/siparislerim.html', {'siparisler': siparisler})


@login_required
@role_required('garson')
@login_required
@role_required('garson')
def siparis_odendi(request, siparis_id):
    siparis = get_object_or_404(Siparis, id=siparis_id, odendi=False, kullanici=request.user)

    # Ödeme işlemi
    siparis.odendi = True
    siparis.save()

    # Masayı boş yap
    masa = siparis.masa
    if masa:
        masa.durum = 'bos'
        masa.save()

    # Gelir kaydı oluştur
    from datetime import date
    GelirGider.objects.create(
        tur='gelir',
        tutar=siparis.toplam_tutar,
        aciklama=f"Sipariş {siparis.id} ödeme kaydı",
        tarih=date.today()
    )

    messages.success(request, "Sipariş ödendi, masa boşaltıldı ve gelir kaydedildi.")
    return redirect(f'/garson-panel/?masa_id={masa.id}' if masa else '/garson-panel/')

def custom_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.rol == 'garson':
                return redirect('garson_panel')
            elif user.rol == 'sef':
                return redirect('sef_panel')
            elif user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('index')
        else:
            context = {'error': 'Kullanıcı adı veya şifre yanlış'}
            return render(request, 'restaurant/login.html', context)
    else:
        return render(request, 'restaurant/login.html')


@login_required
def giris_yonlendirme(request):
    if request.user.rol == 'admin':
        return redirect('/admin/')
    elif request.user.rol == 'sef':
        return redirect('/sef-panel/')
    elif request.user.rol == 'garson':
        return redirect('/garson-panel/')
    else:
        return redirect('/')  # ya da hata sayfası
    
@login_required
def siparis_listesi(request):
    siparisler = Siparis.objects.all().order_by('-tarih_saat')
    return render(request, 'restaurant/siparis_listesi.html', {'siparisler': siparisler})
    


@login_required
@role_required(['garson'])
def siparis_gonder(request):
    if request.method == 'POST':
        masa_no = request.POST.get('masa')
        yemek_ids = request.POST.getlist('yemek')
        adetler = request.POST.getlist('adet')

        if not masa_no or not yemek_ids or not adetler:
            messages.error(request, 'Lütfen tüm alanları doldurunuz.')
            return redirect('garson_panel')

        toplam = Decimal('0.00')
        siparis_ogeleri = []

        for yemek_id, adet in zip(yemek_ids, adetler):
            try:
                menu = Menu.objects.get(id=yemek_id)
                adet = int(adet)
                toplam += menu.fiyat * adet
                siparis_ogeleri.append((menu, adet))
            except:
                continue

        siparis = Siparis.objects.create(
            masa_no=masa_no,
            toplam_tutar=toplam,
            kullanici=request.user,
            durum='hazırlanıyor'
        )

        for menu, adet in siparis_ogeleri:
            SiparisOgeleri.objects.create(
                siparis=siparis,
                menu=menu,
                adet=adet
            )

        masa = Masa.objects.get(numara=masa_no)
        masa.durum = 'dolu'
        masa.save()

        messages.success(request, 'Sipariş başarıyla gönderildi.')
        return redirect('siparislerim')

    return redirect('garson_panel')
        

def kategori_urunleri_getir(request, kategori):
    # Kategori parametresi ile filtrele
    urunler = Menu.objects.filter(kategori=kategori)
    data = []
    for u in urunler:
        data.append({
            "id": u.id,
            "ad": u.yemek_adi,
            "fiyat": float(u.fiyat),
        })
    return JsonResponse(data, safe=False)
    


@login_required
@role_required('sef')
def malzeme_kontrol_ve_kullan(request, siparis_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    siparis = get_object_or_404(Siparis, id=siparis_id)
    
    # İşlemleri atomik yapalım ki hata olursa rollback olsun
    with transaction.atomic():
        # Gerekli malzemelerin toplam miktarını hesapla
        malzeme_ihtiyaci = {}

        for og in siparis.ogeler.all():
            tarif = og.menu.tarif
            if not tarif:
                # Eğer tarif yoksa malzeme kontrolü yapamayız, uyar
                messages.error(request, f"'{og.menu.yemek_adi}' ürünü için tarif tanımlı değil!")
                return redirect('sef_panel')
            
            for tarif_malzeme in tarif.tarifmalzemesi_set.all():
                stok_malzeme = tarif_malzeme.stok
                ihtiyac_miktar = tarif_malzeme.miktar * og.adet

                # Sözlükte topla (aynı malzeme farklı ürünlerde olabilir)
                if stok_malzeme.id in malzeme_ihtiyaci:
                    malzeme_ihtiyaci[stok_malzeme.id]['miktar'] += ihtiyac_miktar
                else:
                    malzeme_ihtiyaci[stok_malzeme.id] = {
                        'stok_obj': stok_malzeme,
                        'miktar': ihtiyac_miktar
                    }

        # Stok kontrolü
        yetersiz_malzeme_listesi = []
        for malzeme_id, veri in malzeme_ihtiyaci.items():
            if veri['stok_obj'].miktar < veri['miktar']:
                yetersiz_malzeme_listesi.append(f"{veri['stok_obj'].malzeme_adi} (İhtiyaç: {veri['miktar']}, Stok: {veri['stok_obj'].miktar})")

        if yetersiz_malzeme_listesi:
            mesaj = "Yetersiz malzemeler:\n" + "\n".join(yetersiz_malzeme_listesi)
            messages.error(request, mesaj)
            return redirect('sef_panel')

        # Stoktan düşme işlemi
        for malzeme_id, veri in malzeme_ihtiyaci.items():
            stok_malzeme = veri['stok_obj']
            stok_malzeme.miktar -= veri['miktar']
            stok_malzeme.save()

        # Sipariş durumunu güncelle
        siparis.durum = 'hazırlanıyor'
        siparis.save()

        messages.success(request, f"Sipariş {siparis.id} için malzemeler kullanıldı, hazırlamaya başlandı.")

    return redirect('sef_panel')
    
def gunluk_satis_raporu(request):
        bugun = date.today()
        son_7_gun = bugun - timedelta(days=6)  # Son 7 gün (bugün dahil)

        satislar = (
            Siparis.objects.filter(tarih__date__gte=son_7_gun)
            .annotate(gun=TruncDate('tarih'))
            .values('gun')
            .annotate(toplam=Sum('toplam_tutar'))
            .order_by('gun')
    )

        # Tarih ve tutarları ayrı listelere ayır
        tarih_listesi = [s['gun'].strftime('%Y-%m-%d') for s in satislar]
        tutar_listesi = [float(s['toplam']) for s in satislar]

        context = {
            'tarih_listesi': json.dumps(tarih_listesi),
            'tutar_listesi': json.dumps(tutar_listesi),
        }
        return render(request, 'restaurant/gunluk_satis_raporu.html', context)

def yeni_siparis(request):
    # Gerekli işlemler
    return render(request, 'restaurant/yeni_siparis.html')



@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Başarıyla çıkış yaptınız.")
    return redirect('login') 



def admin_mi(user):
    return user.rol == 'admin'

@login_required
@user_passes_test(admin_mi)
def gelir_grafik_veri(request):
    veriler = (
        Siparis.objects
        .annotate(gun=TruncDay('tarih'))
        .values('gun')
        .annotate(toplam=Sum('toplam_tutar'))
        .order_by('gun')
    )

    tarih_listesi = [v['gun'].strftime('%Y-%m-%d') for v in veriler]
    tutar_listesi = [float(v['toplam']) for v in veriler]

    return JsonResponse({
        'tarihler': tarih_listesi,
        'tutarlar': tutar_listesi,
    })


def gelir_grafik_veri(request):
    veriler = (
        GelirGider.objects
        .filter(tur='gelir')
        .annotate(gun=TruncDay('tarih'))
        .values('gun')
        .annotate(toplam=Sum('tutar'))
        .order_by('gun')
    )

    tarih_listesi = [v['gun'].strftime('%Y-%m-%d') for v in veriler]
    tutar_listesi = [float(v['toplam']) for v in veriler]

    return JsonResponse({
        'tarihler': tarih_listesi,
        'tutarlar': tutar_listesi,
    })


@login_required
@user_passes_test(admin_mi)
def gelir_raporu_sayfasi(request):
    return render(request, 'restaurant/gelir_raporu.html')



