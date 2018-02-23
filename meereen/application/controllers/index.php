<?php

class IndexController extends Yaf_Controller_Abstract {

    public function indexAction() { // 默认Action
        die('Hello World');
    }

    public function errorAction() {
        $this->getView()->display('Index/error.html');
    }
}