<?php
$db = new SQLite3('iot_data.db');
$result = $db->query('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10');
$data = array();
while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
    $data[] = $row;
}
echo json_encode($data);
?>