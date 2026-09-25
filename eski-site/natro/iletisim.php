<?php
// ESEA Agency – iletişim / proforma (PDA) formu.
// PHP 7.4+ ile uyumludur. main.js formu fetch ile gönderir ve JSON bekler; JS kapalıysa sayfaya ?form=ok|err ile döner.

declare(strict_types=1);

date_default_timezone_set('Europe/Istanbul');
header_remove('X-Powered-By');

const ALICI = 'agency@eseaagency.com';
const GONDEREN = 'agency@eseaagency.com'; // SMTP ile oturum açılan hesap
// SMTP şifresi web'den erişilemeyen üst klasörde durur (public_html'in bir üstü), depoya girmez.
const AYAR_DOSYASI = __DIR__ . '/../iletisim-ayar.php';
const HATA_DOSYASI = __DIR__ . '/../iletisim-hata.log';

$json = strpos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false;
$lang = ($_POST['lang'] ?? 'tr') === 'en' ? 'en' : 'tr';

function bitir(bool $ok, string $hata = ''): void
{
    global $json, $lang;
    if ($json) {
        http_response_code($ok ? 200 : 400);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $hata], JSON_UNESCAPED_UNICODE);
    } else {
        $geri = $lang === 'en' ? '/en/' : '/';
        header('Location: ' . $geri . '?form=' . ($ok ? 'ok' : 'err') . '#iletisim', true, 303);
    }
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST', true, 405);
    exit;
}

// Bot tuzağı: gizli "website" alanı doluysa sessizce başarılı dön.
if (trim((string)($_POST['website'] ?? '')) !== '') {
    bitir(true);
}

// Basit hız sınırı: aynı IP'den 60 saniyede bir gönderim.
$ipDosya = sys_get_temp_dir() . '/esea_form_' . md5($_SERVER['REMOTE_ADDR'] ?? '');
if (is_file($ipDosya) && time() - (int)filemtime($ipDosya) < 60) {
    bitir(false, 'rate_limited');
}

$alan = static function (string $ad, int $max = 200): string {
    $v = trim((string)($_POST[$ad] ?? ''));
    $v = str_replace(["\r", "\0"], '', $v);
    return function_exists('mb_substr') ? mb_substr($v, 0, $max) : substr($v, 0, $max);
};

$ad      = $alan('ad');
$firma   = $alan('firma');
$eposta  = $alan('eposta');
$telefon = $alan('telefon', 60);
$gemi    = $alan('gemi');
$liman   = $alan('liman');
$eta     = $alan('eta', 40);
$hizmet  = $alan('hizmet');
$mesaj   = $alan('mesaj', 5000);
$kvkk    = isset($_POST['kvkk']);

if ($ad === '' || $mesaj === '' || !$kvkk || !filter_var($eposta, FILTER_VALIDATE_EMAIL)) {
    bitir(false, 'invalid');
}
// Başlık enjeksiyonuna karşı: tek satırlık alanlarda satır sonu olmamalı.
foreach ([$ad, $firma, $eposta, $telefon, $gemi, $liman, $eta, $hizmet] as $v) {
    if (strpos($v, "\n") !== false) {
        bitir(false, 'invalid');
    }
}

$satirlar = [
    'Ad Soyad'       => $ad,
    'Firma'          => $firma,
    'E-posta'        => $eposta,
    'Telefon'        => $telefon,
    'Gemi adı / IMO' => $gemi,
    'Liman'          => $liman,
    'ETA'            => $eta,
    'Hizmet'         => $hizmet,
    'Dil'            => strtoupper($lang),
];
$govde = '';
foreach ($satirlar as $k => $v) {
    if ($v !== '') {
        $govde .= $k . ':' . str_repeat(' ', max(1, 16 - mb_strlen($k))) . $v . "\n";
    }
}
$govde .= "\nMesaj:\n" . $mesaj . "\n\n--\n"
    . 'Gönderim: ' . date('d.m.Y H:i') . ' · IP: ' . ($_SERVER['REMOTE_ADDR'] ?? '-') . "\n"
    . "KVKK aydınlatma metni onaylandı.\n";

$konuMetni = 'Web formu: ' . ($gemi !== '' ? $gemi . ' – ' : '') . ($liman !== '' ? $liman . ' – ' : '') . $ad;
$konu = '=?UTF-8?B?' . base64_encode($konuMetni) . '?=';

$basliklar = [
    'Date: ' . date('r'),
    'From: =?UTF-8?B?' . base64_encode('ESEA Agency Web') . '?= <' . GONDEREN . '>',
    'To: <' . ALICI . '>',
    'Reply-To: ' . $eposta,
    'Subject: ' . $konu,
    'Message-ID: <' . bin2hex(random_bytes(12)) . '@eseaagency.com>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
];
$ileti = implode("\r\n", $basliklar) . "\r\n\r\n" . chunk_split(base64_encode($govde));

try {
    $ayar = is_file(AYAR_DOSYASI) ? require AYAR_DOSYASI : null;
    if (!is_array($ayar)) {
        throw new RuntimeException('SMTP ayar dosyası bulunamadı: ' . AYAR_DOSYASI);
    }
    smtpGonder($ayar, GONDEREN, ALICI, $ileti);
    @touch($ipDosya);
    bitir(true);
} catch (Throwable $e) {
    @file_put_contents(HATA_DOSYASI, date('c') . ' ' . $e->getMessage() . "\n", FILE_APPEND);
    bitir(false, 'mail_failed');
}

/**
 * Kimlik doğrulamalı SMTP ile tek bir ileti gönderir (PHP mail() Natro'da kapalı).
 * $ayar: host, port, guvenlik ('ssl' = 465, 'tls' = 587 STARTTLS), kullanici, sifre
 */
function smtpGonder(array $ayar, string $kimden, string $kime, string $ileti): void
{
    $guvenlik = $ayar['guvenlik'] ?? 'ssl';
    $port = (int)($ayar['port'] ?? ($guvenlik === 'ssl' ? 465 : 587));
    $ctx = stream_context_create(['ssl' => [
        'verify_peer' => $ayar['sertifika_dogrula'] ?? true,
        'verify_peer_name' => $ayar['sertifika_dogrula'] ?? true,
        'SNI_enabled' => true,
    ]]);
    $adres = ($guvenlik === 'ssl' ? 'ssl://' : 'tcp://') . $ayar['host'] . ':' . $port;
    $s = @stream_socket_client($adres, $no, $hata, 15, STREAM_CLIENT_CONNECT, $ctx);
    if (!$s) {
        throw new RuntimeException("Bağlantı kurulamadı ($adres): $hata");
    }
    stream_set_timeout($s, 15);
    $oku = static function () use ($s): string {
        $yanit = '';
        while (($satir = fgets($s, 1024)) !== false) {
            $yanit .= $satir;
            if (strlen($satir) < 4 || $satir[3] === ' ') {
                break;
            }
        }
        return $yanit;
    };
    // $etiket: hata kaydına yazılacak ad. Kullanıcı adı/şifre satırları asla kayda geçmez.
    $komut = static function (?string $c, int $beklenen, ?string $etiket = null) use ($s, $oku): string {
        if ($c !== null) {
            fwrite($s, $c . "\r\n");
        }
        $y = $oku();
        if ((int)substr($y, 0, 3) !== $beklenen) {
            $goster = $etiket ?? ($c === null ? 'bağlantı' : (strlen($c) < 80 ? $c : 'DATA'));
            throw new RuntimeException("SMTP beklenmeyen yanıt [$goster]: " . trim($y));
        }
        return $y;
    };
    $komut(null, 220);
    $komut('EHLO eseaagency.com', 250);
    if ($guvenlik === 'tls') {
        $komut('STARTTLS', 220);
        if (!stream_socket_enable_crypto($s, true, STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT | STREAM_CRYPTO_METHOD_TLSv1_3_CLIENT)) {
            throw new RuntimeException('STARTTLS başarısız');
        }
        $komut('EHLO eseaagency.com', 250);
    }
    $komut('AUTH LOGIN', 334);
    $komut(base64_encode($ayar['kullanici']), 334, 'kullanıcı adı');
    $komut(base64_encode($ayar['sifre']), 235, 'şifre');
    $komut('MAIL FROM:<' . $kimden . '>', 250);
    $komut('RCPT TO:<' . $kime . '>', 250);
    $komut('DATA', 354);
    // Nokta ile başlayan satırlar SMTP'de ikiye katlanır (base64 gövdede zaten olmaz).
    $komut(preg_replace('/^\./m', '..', $ileti) . "\r\n.", 250, 'DATA');
    fwrite($s, "QUIT\r\n");
    fclose($s);
}
