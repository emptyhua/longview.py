longview.py
===========

get_report_example.php
~~~
$report = @$_POST['report'];
$gzip   = @$_POST['gzip'];
if (!isset($report)) {
    die('require $report');
}

if (strcmp($gzip, 'on') === 0) {
    $report = gzuncompress($report);
    if ($report === false) {
        die('gzuncompress failed');
    }
}

$report = @json_decode($report, true);
if (is_null($report)) {
    die('report json_decode failed');
}

var_dump($report);
~~~
