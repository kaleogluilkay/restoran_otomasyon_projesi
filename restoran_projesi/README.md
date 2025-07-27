##  Geliştirici

- GitHub: [@kaleogluilkay](https://github.com/kaleogluilkay)
- Fatma Zehra Demirci
---

# Restoran Stok Takip ve Sipariş Yönetim Sistemi
Bu proje bir restoranın stok takibini yapmak, yemek tariflerini yönetmek, sipariş alma sürecini düzenlemek ve satış raporlarını sunmak amacıyla geliştirilmiştir.

 ## Kullanıcı Rolleri
 
**Admin:** Kullanıcı, stok, menü, tarif ve rapor modüllerini yönetebilir.
**Şef:** Tarif oluşturur, stok malzemelerini görüntüler, sipariş durumlarını günceller.
**Garson:** Masa seçip menüden sipariş oluşturur, sipariş durumunu takip eder.

## Özellikler

### Kullanıcı Yönetimi (Admin)
-Kullanıcı oluşturma, silme, güncelleme
-Rollere göre yetki kontrolü 

### Stok Modülü (Admin, Şef)
-Malzeme ekleme, güncelleme, silme
-Birim türü yönetimi (kg,litre,adet vs.)

### Tarif Modülü (Admin, Şef)
-Tarif oluşturma, içerik ekleme
-Malzeme miktarlarının ayarlanması 

### Menü Modülü (Admin, Garson)
-Menüye yemek ekleme
-Yemek-fiyat ilişkilendirme
-Tarif ile bağlantı kurma

### Sipariş Modülü (Garson, Şef, Admin)
-Masa seçimi ve sipariş oluşturma
-Siparişin şef paneline iletilmesi
-Sipariş durumu takibi (Bekliyor, Hazırlanıyor, Hazır)
-Ödeme ve sipariş tamamlama

### Raporlama Modülü (Admin)
-Günlük satış roporları
-Chart.js ile görselleştirme


## Kullanılan Teknolojiler 

- **Python 3.11**
- **Django 5.2.3**
- **MySQL**
- **HTML5, CSS3, Javascript**
- **Chart.js** - Grafik gösterimi
- **Bootstrap** - Arayüz tasarımı

## Kurulum 
### 1- Gerekli Kurulumlar 
Proje Django ve MySQL kullanmaktadır. Öncelikle aşağıdaki bileşenlerin sisteminizde kurulu olması gerekir:
- [Python 3.11+] (https://www.python.org/downloads/)
- [MySQL Server] (https://dev.mysql.com/downloads/mysql/)
- [MySQL Workbench] (https://dev.mysql.com/downloads/workbench/)
- [Git] (https://git-scm.com/) 

## 2. Projeyi Klonlayın (veya ZIP’ten çıkarın)
--Git yüklü ise terminalde: 
git clone https://github.com/kaleogluilkay/restoran_projesi.git
cd restoran_projesi
--Git yoksa, GitHub üzerinden "Code > Download ZIP" diyerek indirebilirsiniz.

### 3 - Sanal Ortam Oluşturma 
python -m venv env

## 4- Aktif Etme
### Windows: 
venv\Scripts\activate
### Mac/Linux:
source venv/bin/activate

## 5- Gerekli Paketleri Yükleme
pip install django mysqlclient 
(Alternatif olarak, uyumsuzluk durumunda PyMySQL kullanılabilir.)

## 6- MySQL Veritabanı Oluşturun
MySQL’e bağlanarak yeni bir veritabanı oluşturun:
(CREATE DATABASE restoran_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;)

### 7. settings.py Ayarlarını Yapın
restoran_projesi/settings.py dosyasındaki DATABASES bölümünü şu şekilde düzenleyin:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'restoran_db',
        'USER': 'kendi_mysql_kullanici_adiniz',
        'PASSWORD': 'kendi_mysql_sifreniz',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

## 8. Veritabanı Tablolarını Oluşturun
python manage.py makemigrations
python manage.py migrate

## 9. Süper Kullanıcı Oluşturun
python manage.py createsuperuser

## 10. Uygulamayı Başlatın
python manage.py runserver

Tarayıcınızdan http://127.0.0.1:8000/ adresine giderek uygulamayı kullanmaya başlayabilirsiniz.







