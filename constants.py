"""Uygulama genelinde kullanılan sabitler ve açıklama metinleri."""

from __future__ import annotations

APP_TITLE = "Makine Öğrenmesi Tabanlı Ağ Saldırı Tespit Sistemi"
MODEL_FILE_NAME = "network_attack_detector.pkl"
RESULT_COLUMNS = ("Tahmin", "Risk Seviyesi")

ATTACK_NAMES = {
    0: "Benign",
    1: "Bot",
    2: "DDoS",
    3: "DoS GoldenEye",
    4: "DoS Hulk",
    5: "DoS Slowhttptest",
    6: "DoS Slowloris",
    7: "FTP-Patator",
    8: "Heartbleed",
    9: "Infiltration",
    10: "PortScan",
    11: "SSH-Patator",
    12: "Web Attack Brute Force",
    13: "Web Attack SQL Injection",
    14: "Web Attack XSS",
}

RISK_MAP = {
    "Benign": "Düşük",
    "Bot": "Kritik",
    "DDoS": "Yüksek",
    "DoS GoldenEye": "Kritik",
    "DoS Hulk": "Yüksek",
    "DoS Slowhttptest": "Yüksek",
    "DoS Slowloris": "Yüksek",
    "FTP-Patator": "Orta",
    "SSH-Patator": "Orta",
    "Heartbleed": "Kritik",
    "Infiltration": "Kritik",
    "PortScan": "Yüksek",
    "Web Attack Brute Force": "Kritik",
    "Web Attack SQL Injection": "Kritik",
    "Web Attack XSS": "Yüksek",
}

ATTACK_DESCRIPTIONS = {
    "Bot": (
        "Ele geçirilmiş bir cihazın uzaktan komutlarla kötü amaçlı "
        "faaliyetlerde kullanılmasını ifade eder."
    ),
    "DDoS": (
        "Çok sayıda kaynaktan yoğun trafik göndererek hedef sistemi "
        "hizmet veremez hâle getirmeyi amaçlar."
    ),
    "DoS GoldenEye": (
        "HTTP bağlantılarını tüketerek web sunucusunun yeni isteklere "
        "yanıt vermesini engellemeye çalışan DoS saldırısıdır."
    ),
    "DoS Hulk": (
        "Yoğun ve değişken HTTP istekleri göndererek sistemi hizmet "
        "veremez hâle getiren DoS saldırısıdır."
    ),
    "DoS Slowhttptest": (
        "HTTP bağlantılarını uzun süre açık tutup sunucu kaynaklarını "
        "tüketmeye yönelik yavaş DoS saldırısıdır."
    ),
    "DoS Slowloris": (
        "Eksik HTTP istekleriyle çok sayıda bağlantıyı açık tutarak web "
        "sunucusunun kapasitesini tüketir."
    ),
    "FTP-Patator": (
        "FTP hesaplarına karşı çok sayıda kullanıcı adı ve parola "
        "denemesi yapan kaba kuvvet saldırısıdır."
    ),
    "Heartbleed": (
        "Savunmasız OpenSSL sürümlerindeki bellek sızıntısı açığını "
        "kullanarak hassas verileri elde etmeyi amaçlar."
    ),
    "Infiltration": (
        "Saldırganın sisteme sızdıktan sonra iç ağda yetkisiz faaliyet "
        "yürütmesini ve kalıcılık sağlamasını ifade eder."
    ),
    "PortScan": (
        "Hedef sistem üzerindeki açık portları ve çalışan servisleri "
        "tespit etmeye yönelik keşif saldırısıdır."
    ),
    "SSH-Patator": (
        "SSH hesaplarına karşı çok sayıda kimlik bilgisi deneyerek "
        "yetkisiz erişim sağlamayı amaçlar."
    ),
    "Web Attack Brute Force": (
        "Web uygulaması giriş ekranlarında çok sayıda parola denemesiyle "
        "hesap erişimi elde etmeyi amaçlar."
    ),
    "Web Attack SQL Injection": (
        "Veritabanına zararlı SQL sorguları göndererek yetkisiz erişim "
        "veya veri manipülasyonu sağlamayı amaçlar."
    ),
    "Web Attack XSS": (
        "Web sayfasına zararlı istemci tarafı kodu enjekte ederek "
        "kullanıcı oturumlarını veya verilerini hedefler."
    ),
}

SECURITY_RECOMMENDATIONS = {
    "Bot": [
        "Şüpheli dış bağlantıları ve komuta-kontrol trafiğini engelleyin.",
        (
            "Uç nokta güvenlik çözümlerini güncelleyin ve tam tarama "
            "çalıştırın."
        ),
    ],
    "DDoS": [
        "DDoS koruması, trafik sınırlama ve yük dengeleme kullanın.",
        "Anormal trafik üreten IP adreslerini geçici olarak engelleyin.",
    ],
    "DoS GoldenEye": [
        "Web sunucusu bağlantı ve istek limitlerini sıkılaştırın.",
        "WAF ve ters proxy üzerinde oran sınırlama kuralları uygulayın.",
    ],
    "DoS Hulk": [
        "HTTP isteklerine oran sınırlama ve davranış tabanlı filtre ekleyin.",
        "IDS/IPS imzalarını ve web sunucusu koruma kurallarını güncelleyin.",
    ],
    "DoS Slowhttptest": [
        "Bağlantı zaman aşımı ve eş zamanlı bağlantı limitlerini azaltın.",
        "Yavaş HTTP saldırılarını algılayan WAF kurallarını etkinleştirin.",
    ],
    "DoS Slowloris": [
        "Eksik HTTP istekleri için kısa zaman aşımı değerleri belirleyin.",
        "Ters proxy veya yük dengeleyici üzerinden bağlantı sınırı uygulayın.",
    ],
    "FTP-Patator": [
        "FTP oturum açma denemelerine hız sınırı ve hesap kilitleme ekleyin.",
        "Mümkünse FTP yerine güvenli dosya aktarım protokolleri kullanın.",
    ],
    "Heartbleed": [
        "Savunmasız OpenSSL sürümlerini derhâl güncelleyin.",
        "Sertifikaları, özel anahtarları ve etkilenmiş parolaları yenileyin.",
    ],
    "Infiltration": [
        "Etkilenen cihazı ağdan izole edin ve olay müdahalesi başlatın.",
        (
            "Yetkisiz hesap, kalıcılık mekanizması ve yanal hareket "
            "izlerini inceleyin."
        ),
    ],
    "PortScan": [
        "Gereksiz portları kapatın ve firewall kurallarını güncelleyin.",
        "Tarama yapan IP adreslerini izleyin veya geçici olarak engelleyin.",
    ],
    "SSH-Patator": [
        (
            "SSH parola girişini sınırlandırın ve anahtar tabanlı "
            "kimlik doğrulayın."
        ),
        "Başarısız girişler için hesap kilitleme veya Fail2ban kullanın.",
    ],
    "Web Attack Brute Force": [
        "Çok faktörlü kimlik doğrulama ve hesap kilitleme politikası kullanın.",
        "Giriş denemelerine hız sınırı ve bot koruması ekleyin.",
    ],
    "Web Attack SQL Injection": [
        "Parametreli sorgular kullanın ve kullanıcı girdilerini doğrulayın.",
        "WAF üzerinde SQL Injection koruma kurallarını etkinleştirin.",
    ],
    "Web Attack XSS": [
        (
            "Çıktı kodlama, girdi doğrulama ve içerik güvenlik "
            "politikası uygulayın."
        ),
        "Web uygulaması bağımlılıklarını ve WAF kurallarını güncelleyin.",
    ],
}

GENERAL_RECOMMENDATIONS = [
    "Firewall kurallarını düzenli olarak gözden geçirin.",
    "IDS/IPS sistemlerini aktif tutun ve imzalarını güncelleyin.",
    "Şüpheli IP adreslerini ve olağan dışı ağ trafiğini izleyin.",
    "İşletim sistemi, servis ve uygulama yamalarını zamanında uygulayın.",
]

RISK_COLORS = {
    "Düşük": "#2E8B57",
    "Orta": "#D99A2B",
    "Yüksek": "#E56B3F",
    "Kritik": "#C73E4D",
}



PROTOCOL_NAMES = {
    1: "ICMP",
    2: "IGMP",
    6: "TCP",
    17: "UDP",
    41: "IPv6",
    47: "GRE",
    50: "ESP",
    51: "AH",
    58: "ICMPv6",
    89: "OSPF",
    132: "SCTP",
}

PCAP_EXTENSIONS = {".pcap", ".pcapng"}
PCAP_DEFAULT_COLUMNS = [
    "src_ip",
    "src_port",
    "dst_ip",
    "dst_port",
    "protocol_name",
    "application_name",
    "bidirectional_duration_ms",
    "bidirectional_packets",
    "bidirectional_bytes",
    "src2dst_packets",
    "src2dst_bytes",
    "dst2src_packets",
    "dst2src_bytes",
]

PORT_SCAN_UNIQUE_PORT_THRESHOLD = 20
DENSE_TCP_FLOW_MINIMUM = 50
DENSE_TCP_RATIO_THRESHOLD = 0.80
HIGH_TRANSFER_TOTAL_BYTES = 100 * 1024 * 1024
HIGH_TRANSFER_AVERAGE_BYTES = 2 * 1024 * 1024
