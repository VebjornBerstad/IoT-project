<?php
$db = new SQLite3('iot_data.db');

$output = exec('/var/www/html/venv/bin/python /var/www/html/read_sensor.py');

// Print the output for debugging
echo "Python script output: " . $output;

$sensorData = json_decode($output, true);
$humidity = $sensorData['humidity'];
$temperature = $sensorData['temperature'];
$outsideTemperature = $sensorData['outside_temperature'];

$inputData = [];
$windowStatus = 0;
$ovenTemperature = 0;

if (file_exists('user_input.json')) {
    $jsonData = file_get_contents('user_input.json');
    if (!empty($jsonData)) {
        $inputData = json_decode($jsonData, true);
        $windowStatus = $inputData['window_status'] ?? 0;
        $ovenTemperature = $inputData['oven_temperature'] ?? 0;
    }
}


$stmt = $db->prepare('INSERT INTO sensor_data (temperature, humidity, oven_temperature, window_status, outside_temperature) VALUES (?, ?, ?, ?, ?)');
$stmt->bindValue(1, $temperature, SQLITE3_FLOAT);
$stmt->bindValue(2, $humidity, SQLITE3_FLOAT);
$stmt->bindValue(3, $ovenTemperature, SQLITE3_INTEGER);
$stmt->bindValue(4, $windowStatus, SQLITE3_INTEGER);
$stmt->bindValue(5, $outsideTemperature, SQLITE3_FLOAT);

if (!$stmt->execute()) {
    echo "Error inserting data into the database: " . $db->lastErrorMsg();
} else {
    echo "Data inserted successfully";
}

?>