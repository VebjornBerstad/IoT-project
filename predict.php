<?php
// Execute the Python script to generate predictions
$predictions_output = exec('/var/www/html/venv/bin/python /var/www/html/predict.py');
$predictions = json_decode($predictions_output, true);

// Return the predictions as JSON
header('Content-Type: application/json');
echo json_encode($predictions);
?>