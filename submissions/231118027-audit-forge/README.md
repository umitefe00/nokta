# Challenge: Audit-Forge
**Öğrenci:** Ümit Efe Özkaleli  
**Öğrenci No:** 231118027  
**Üniversite:** Samsun Üniversitesi - Yazılım Mühendisliği  
**Seçilen Track:** Track A (Sadelik ve Drop-in Disiplini)

---

## 📌 Proje Hakkında ve Karar Günlüğü (Decision Log)
Bu proje, React Native / Expo tabanlı bir mobil uygulamanın içine `@xtatistix/mobile-audit` widget'ının "Self-contained" modda gömülmesini ve üretilen Markdown bug raporlarının otonom yapay zeka ajanları tarafından tamir edilmesini simüle eden uçtan uca bir sistemdir.

### Alınan Mimari Kararlar:
1. **Drop-in Sınır Koruması:** Widget uygulamanın kök dizinine (`App.tsx`) navigasyon yapısını bozmayacak şekilde entegre edilmiştir. Uygulamanın diğer bileşenleri widget'ın varlığından tamamen bağımsızdır.
2. **Web Ortamı ve Donanım Uyumluluğu (Hack):** Proje geliştirme aşamasında web tarayıcısı (`localhost`) üzerinde test edilirken native donanım paketlerinin (`react-native-view-shot` ve `expo-file-system`) çökmesini engellemek için `captureScreen` ve `captureRef` fonksiyonları mock/dummy base64 görsellerle kandırılmış, üretilen `.md` raporu `console.log` ile doğrudan geliştirici konsoluna yönlendirilerek kayıpsız olarak kurtarılmıştır.
3. **Avatar Modülü (Bypass):** 3D Avatar sahnesi (`AvatarScene.tsx`) `.glb` modeli ile kodlanmış olmasına rağmen, Expo Web ortamında Metro Bundler'ın `Three.js` paketlerindeki `import.meta` ECMAScript standartlarını derleyememesi sebebiyle kasıtlı olarak devreden çıkarılmış (bypass), uygulamanın çekirdek kararlılığı (ses ve STT) korunmuştur.

---

## 🔗 Linkler & Çıktılar
- **Expo QR Link / Demo:** 
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█ ▄▄▄▄▄ █▀ █▀▀█ ▀ ▄▀▄▀█ ▄▄▄▄▄ █
█ █   █ █▀ ▄ ███▀█▀ ▀▄█ █   █ █
█ █▄▄▄█ █▀█ █▄ ▀▀ █▀▄▀█ █▄▄▄█ █
█▄▄▄▄▄▄▄█▄█▄█ ▀▄▀ █ █ █▄▄▄▄▄▄▄█
█▄▄  ▄▀▄   ▄█▄█▄▄▀ ▄▀▀ ▀ ▀▄▀▄▀█
██ █▀▀ ▄▀▀ ▀ ▄█▀▄██ ▀▀▄▄▄██▄ ██
█▄▄█▀▄▄▄  ▄▀▄▀▀▀▄ ▄▄▀▀ ▀▀▀▀ ▄▀█
█ █▄▀▀▄▄██▀▀█▀ ▄ ▄█▄█ █▄▀ ▄▄▀██
█ █ ▀▄█▄ ▄█▀█▄█▄█▀  ▀▀█▀ ▀▀ ▄ █
█ █▀  █▄▀  █ ▄█▀ ▀▄▀█▀██ █ ▄███
█▄█▄▄██▄▄  ▄▄▀▀▀▄▀▄▀▀ ▄▄▄ █ ▀▀█
█ ▄▄▄▄▄ █▄▄▀█▀ ▄▄▀██  █▄█ ▀▄███
█ █   █ █  ▀█▄█▄██ █▀▄▄▄▄▄█ ▀▀█
█ █▄▄▄█ █ ▀▀ ▄█▀ ██ █ ▄   ▀█ ██
█▄▄▄▄▄▄▄█▄▄▄▄███▄▄▄█▄████▄█▄███

- **60 Sn Demo Video Linki:** [https://youtube.com/shorts/wSptYw8QACU?feature=share]

---

## 🚀 Özellikler ve Aşamalar (Phases)

### Phase A: Ses Analizi ve Dikte (Voice to STT)
* **Web Audio API (FFT/RMS):** Mikrofon dinlenerek ses şiddeti anlık olarak analiz edilmiş ve görsel barlara (Voice Visualizer) kayıpsız yansıtılmıştır. Sessizlikte sönen, seste canlanan akıcı bir animasyon sağlanmıştır.
* **Speech-To-Text (STT):** Kullanıcının sesi Web Speech API kullanılarak anlık olarak yazıya dökülüp (dikte) AuditWidget raporlarına beslenmek üzere metin kutusuna aktarılmaktadır.

### Phase B & C: Forge Döngüsü ve Expert Bridge (STUCK Durumu)
* Sistemin Agent onarım döngüleri simüle edilmiş ve kayıtları **`FORGE.md`** dosyasına işlenmiştir.
* Agent'ın kasıtlı olarak 2 döngü üst üste çözemediği (FAIL) sorunlarda sistem **STUCK** durumuna düşmektedir.
* STUCK anında **ExpertBridge** bileşeni devreye girerek Jitsi üzerinden doğrudan WebRTC tabanlı bir uzman çağrısı (görüntülü görüşme & ekran paylaşımı) başlatır. Uzman görüşmesinin özeti **`BRIDGE.md`** dosyasında belgelenmiştir.

---

## 🛠️ Kurulum ve Çalıştırma

Projenin bağımlılıklarını yüklemek ve önbelleği temizleyerek başlatmak için `app` klasöründe (veya `package.json`'ın bulunduğu dizinde) şu komutları sı