<?php
$json_data = file_get_contents('user_input.json');
$data = json_decode($json_data, true);

$window_status = $data['window_status'] ?? 0;
$oven_temperature = $data['oven_temperature'] ?? 0;

$response = array(
    'window_status' => $window_status,
    'oven_temperature' => $oven_temperature
);

header('Content-Type: application/json');
echo json_encode($response);
?>