<?php

function generateRandomString($length = 10) {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $randomString = '';
    for ($i = 0; $i < $length; $i++) {
        $randomString .= $characters[rand(0, strlen($characters) - 1)];
    }
    return $randomString;
}

if (count($argv) >= 2 && $argv[1] == "generate") {
    $count = 10;
    $result = [];
    for ($i = 0; $i < $count; $i++) {
        $salt = openssl_random_pseudo_bytes(16);
        $password = generateRandomString(8);
        $pbkdf22hash = hash_pbkdf2('sha512', $password, $salt, 35000, 64);
        $p0 = base64_encode(hex2bin($pbkdf22hash));
        $excepted_hash = password_hash(base64_decode($p0), PASSWORD_BCRYPT);
        $result[] = [$password, base64_encode($salt), $excepted_hash];
    }
    $path = './';
    $filename = 'test.csv';
    if (!is_readable($path)) {
        mkdir($path, 0700, true);
    }
    $bill_log_path = sprintf('%s/%s', $path, $filename);
    $file = fopen($bill_log_path, 'w');
//        $header && fputcsv($file, $header);
    foreach ($result as $b) {
        fputcsv($file, $b);
    }
    fclose($file);
} else {
    $filename = './test.csv';
    $file = fopen($filename, "r");
    $all_data = array();
    while ($data = fgetcsv($file, 1024, ",")) {
        array_push($all_data, $data);
    }
    fclose($file);
    foreach ($all_data as $item) {
        $verify = false;
        $salt = base64_decode($item[1]);
        $password = $item[0];
        $pbkdf22hash = hash_pbkdf2('sha512', $password, $salt, 35000, 64);
        $p0 = base64_encode(hex2bin($pbkdf22hash));
        $excepted_hash = $item[2];
        $verify = password_verify(base64_decode($p0), $excepted_hash);
        var_dump($verify);
        if (!$verify) {
            var_dump($password);
        }
    }
}