/*
* @Author: shanzhu
* @Date:   2017-12-20 15:00:17
* @Last Modified by:   shanzhu
* @Last Modified time: 2018-02-11 09:49:16
*/

CREATE TABLE `user_agent_list`(
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `user_agent` varchar(200) NOT NULL DEFAULT '',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `login_cookie`(
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `url` varchar(1000) NOT NULL DEFAULT '',
    `cookie` varchar(5000) NOT NULL DEFAULT '',
    `expires` int(100) NOT NULL DEFAULT 0,
    PRIMARY key(`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `province` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `province` varchar(100) NOT NULL DEFAULT '',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `city` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `province` int(11) NOT NULL DEFAULT 0,
    `city` varchar(100) NOT NULL DEFAULT '',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `topic` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `item_type` varchar(11) NOT NULL DEFAULT 'video',
    `chs_name` varchar(100) NOT NULL DEFAULT '',
    `eng_name` varchar(100) NOT NULL DEFAULT '',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `user` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `nickname` varchar(100) NOT NULL DEFAULT '',
    `email` varchar(100) NOT NULL,
    `password` varchar(100) NOT NULL,
    `password_raw` varchar(100) NOT NULL,
    `login_in` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`id`) 
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
