<?php
// GEÇİCİ TEŞHİS DOSYASI – hangi SMTP sunucusu/portuna bağlanılabildiğini gösterir.
// E-posta göndermez, şifre kullanmaz. Sonucu aldıktan sonra SİLİN.
header('Content-Type: text/plain; charset=utf-8');
set_time_limit(300);

$hostlar = ['mail.eseaagency.com', 'mx-out05.natrohost.com', 'mail.kurumsaleposta.com', 'localhost'];
$denemeler = [];
foreach ($hostlar as $h) {
    foreach ([[465, 'ssl'], [587, 'tls'], [25, 'tls']] as [$p, $g]) {
        $denemeler[] = [$h, $p, $g];
    }
}

function dene(string $h, int $p, string $g, bool $dogrula): string
{
    $ctx = stream_context_create(['ssl' => [
        'verify_peer' => $dogrula, 'verify_peer_name' => $dogrula,
        'capture_peer_cert' => true, 'SNI_enabled' => true,
    ]]);
    $adres = ($g === 'ssl' ? 'ssl://' : 'tcp://') . "$h:$p";
    $s = @stream_socket_client($adres, $no, $hata, 5, STREAM_CLIENT_CONNECT, $ctx);
    if (!$s) {
        $ssl = '';
        while ($e = openssl_error_string()) {
            $ssl .= " | $e";
        }
        return "BAĞLANAMADI ($no) $hata$ssl";
    }
    stream_set_timeout($s, 8);
    $banner = trim((string)fgets($s, 512));
    $sonuc = "BAĞLANDI · $banner";
    if ($g === 'tls') {
        fwrite($s, "EHLO eseaagency.com\r\n");
        $ehlo = '';
        while (($l = fgets($s, 512)) !== false) {
            $ehlo .= $l;
            if (strlen($l) < 4 || $l[3] === ' ') {
                break;
            }
        }
        $sonuc .= stripos($ehlo, 'STARTTLS') !== false ? ' · STARTTLS var' : ' · STARTTLS YOK';
        $sonuc .= stripos($ehlo, 'AUTH') !== false ? ' · AUTH var' : ' · AUTH yok';
        if (stripos($ehlo, 'STARTTLS') !== false) {
            fwrite($s, "STARTTLS\r\n");
            fgets($s, 512);
            $ok = @stream_socket_enable_crypto($s, true, STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT | STREAM_CRYPTO_METHOD_TLSv1_3_CLIENT);
            $sonuc .= $ok ? ' · TLS OK' : ' · TLS HATASI';
        }
    }
    $prm = stream_context_get_params($s);
    if (!empty($prm['options']['ssl']['peer_certificate'])) {
        $c = openssl_x509_parse($prm['options']['ssl']['peer_certificate']);
        $sonuc .= ' · sertifika: ' . ($c['subject']['CN'] ?? '?');
    }
    fwrite($s, "QUIT\r\n");
    fclose($s);
    return $sonuc;
}

echo "PHP " . PHP_VERSION . " · mail() " . (function_exists('mail') ? 'var' : 'KAPALI') . "\n\n";
foreach ($denemeler as [$h, $p, $g]) {
    $r = dene($h, $p, $g, true);
    // Zaman aşımı/ret dışındaki hatalar (ör. sertifika) için doğrulamasız da dene
    if ((strpos($r, 'BAĞLANAMADI') === 0 && !preg_match('/\((110|111)\)/', $r)) || strpos($r, 'TLS HATASI') !== false) {
        $r .= "\n      doğrulamasız: " . dene($h, $p, $g, false);
    }
    printf("%-26s %-4d %-3s  %s\n", $h, $p, $g, $r);
    flush();
}
