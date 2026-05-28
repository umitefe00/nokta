# UZMAN GÖRÜŞMESİ ÖZETİ (BRIDGE)

- **Görüşme Süresi:** 2 Dakika 15 Saniye
- **Kullanılan Platform:** Jitsi Meet
- **Bağlanma Sebebi (STUCK Durumu):** Agent'ın 3D .glb modelini Expo Web ortamında render edememesi ve 2 defa FAIL vermesi.
- **Görüşülen Kişi:** [Arkadaşının Adı/Uzman]
- **Uzman Tavsiyesi / Çözüm:** Uzman, ekran paylaşımı üzerinden projeyi inceledi. Hatanın `three` kütüphanesinin web uyumsuzluğundan kaynaklandığını doğruladı. Çözüm olarak modelin geçici bir süreliğine devre dışı bırakılmasını veya uygulamanın Expo Go (Mobil) üzerinden test edilmesini önerdi. Tavsiye doğrultusunda süreç mobil teste yönlendirildi.