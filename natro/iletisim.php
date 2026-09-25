<?php
// ESEA Agency – iletişim / proforma (PDA) formu.
// PHP 7.4+ ile uyumludur. main.js formu fetch ile gönderir ve JSON bekler; JS kapalıysa sayfaya ?form=ok|err ile döner.

declare(strict_types=1);

const ALICI = 'agency@eseaagency.com';
const GONDEREN = 'agency@eseaagency.com'; // alan adına ait gerçek bir hesap olmalı (SPF uyumu)

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
        $govde .= str_pad($k . ':', 17) . $v . "\n";
    }
}
$govde .= "\nMesaj:\n" . $mesaj . "\n\n--\n"
    . 'Gönderim: ' . date('d.m.Y H:i') . ' · IP: ' . ($_SERVER['REMOTE_ADDR'] ?? '-') . "\n"
    . "KVKK aydınlatma metni onaylandı.\n";

$konuMetni = 'Web formu: ' . ($gemi !== '' ? $gemi . ' – ' : '') . ($liman !== '' ? $liman . ' – ' : '') . $ad;
$konu = '=?UTF-8?B?' . base64_encode($konuMetni) . '?=';

$basliklar = implode("\r\n", [
    'From: ESEA Agency Web <' . GONDEREN . '>',
    'Reply-To: ' . $eposta,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);

$ok = mail(ALICI, $konu, $govde, $basliklar, '-f' . GONDEREN);
if ($ok) {
    @touch($ipDosya);
}
bitir($ok, $ok ? '' : 'mail_failed');
