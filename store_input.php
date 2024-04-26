<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$json_data = file_get_contents('php://input');
$data = json_decode($json_data, true);

$window_status = $data['window_status'] ?? 0;
$oven_temperature = $data['oven_temperature'] ?? 0;

$data = array(
    'window_status' => $window_status,
    'oven_temperature' => $oven_temperature
);

$json_data = json_encode($data);

if (file_put_contents('user_input.json', $json_data) === false) {
    error_log("Error writing to user_input.json: " . json_last_error_msg());
}
?>