# 🤖 TeleBuild APK - Telegram 24/7 Native APK & Flutter Builder

Sistem otomatisasi build file Android *.APK Native* dan *Flutter* secara **Always-On (24/7)** langsung dari Telegram chat, didukung oleh infrastruktur cloud runner GitHub Actions (16GB RAM, Android SDK 34, Flutter 3.29.x, OpenJDK 17, Gradle).

---

## 🌟 Fitur Baru: Deteksi Otomatis ZIP & Live Log Preview!
1. **Lampirkan File ZIP Langsung:**
   - Cukup seret (drag & drop) atau lampirkan file `.zip` project ke chat bot Telegram.
   - Bot otomatis membaca isi ZIP:
     - Jika ada `pubspec.yaml` ➔ Build menggunakan **Flutter Engine** (`flutter build apk`).
     - Jika ada `build.gradle` ➔ Build menggunakan **Android Gradle Engine** (`./gradlew assembleRelease`).
2. **Live Log Preview Saat Build:**
   - Pesan status di Telegram akan otomatis ter-update secara berkala menampilkan tahap pre-build, compile code, packaging, hingga file siap.
3. **Pengiriman Otomatis:**
   - File `.apk` langsung dikirimkan ke chat Telegram beserta hash SHA-256 untuk verifikasi keamanan.
