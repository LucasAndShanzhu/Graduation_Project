<?php

/**
 * @Author: shanzhu
 * @Date:   2018-02-09 10:49:23
 * @Last Modified by:   shanzhu
 * @Last Modified time: 2018-02-09 10:49:40
 */
date_default_timezone_set('PRC');

define("APP_PATH",  realpath(dirname(__FILE__) . '/../')); /* 指向public的上一级 */
$app = new Yaf_Application(APP_PATH . "/conf/application.ini");
$app->bootstrap()->run();