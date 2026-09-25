<?php
// Bu dosyanın adını iletisim-ayar.php yapıp public_html'in BİR ÜST klasörüne koyun
// (cPanel Dosya Yöneticisi'nde "Home" klasörü). Web'den erişilemez, şifre güvende kalır.
return [
    'host'      => 'mx-out05.natrohost.com', // mail.eseaagency.com'un gerçek sunucusu; sertifikası bu adla eşleşir
    'port'      => 465,
    'guvenlik'  => 'ssl',                 // 465 için 'ssl', 587 için 'tls'
    'kullanici' => 'agency@eseaagency.com',
    'sifre'     => 'BURAYA_AGENCY_EPOSTA_SIFRESI',
    // Sunucu sertifikası alan adıyla eşleşmezse (hata günlüğünde "certificate" geçerse) false yapın:
    'sertifika_dogrula' => true,
];
