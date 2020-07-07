drop database if exists stocks;
create database stocks;
use stocks;
CREATE TABLE `stock_base` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stock_code` varchar(10) DEFAULT NULL,
  `stock_name` varchar(16) DEFAULT NULL,
  `last_price` float DEFAULT NULL,
  `change_pct` float DEFAULT NULL,
  `head_num` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `stock_base_id_uindex` (`id`),
  UNIQUE KEY `stock_base_stock_code_uindex` (`stock_code`)
) ENGINE=InnoDB AUTO_INCREMENT=5358 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;




CREATE TABLE `stock_hot_history` (
  `stock_code` varchar(8) DEFAULT NULL,
  `bef_up_1` float DEFAULT NULL,
  `bef_up_2` float DEFAULT NULL,
  `bef_up_3` float DEFAULT NULL,
  `bef_up_4` float DEFAULT NULL,
  `bef_up_5` float DEFAULT NULL,
  `bef_up_6` float DEFAULT NULL,
  `bef_up_7` float DEFAULT NULL,
  `bef_up_8` float DEFAULT NULL,
  `bef_up_9` float DEFAULT NULL,
  `bef_up_10` float DEFAULT NULL,
  `bef_up_11` float DEFAULT NULL,
  `bef_up_12` float DEFAULT NULL,
  UNIQUE KEY `stock_hot_history_stock_code_uindex` (`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE `theme_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_code` varchar(11) DEFAULT NULL,
  `theme_name` varchar(11) DEFAULT NULL,
  `change_pct` float DEFAULT NULL,
  `type` varchar(11) DEFAULT NULL,
  `description` text,
  `up` int DEFAULT NULL,
  `down` int DEFAULT NULL,
  `fair` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE `theme_stocks_map` (
  `id` int NOT NULL AUTO_INCREMENT,
  `theme_code` varchar(11) DEFAULT NULL,
  `theme_name` varchar(11) DEFAULT NULL,
  `count` int DEFAULT NULL,
  `stock_names` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `theme_hot_theme_code_uindex` (`theme_code`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

create table stocks.theme_hot
(
	id int auto_increment
		primary key,
	theme_code varchar(12) null,
	theme_name varchar(24) null,
	tmp_degree text null,
	bef_degree_1 float null,
	bef_degree_2 float null,
	bef_degree_3 float null,
	bef_degree_4 float null,
	bef_degree_5 float null,
	bef_degree_6 float null,
	bef_degree_7 float null,
	bef_degree_8 float null,
	bef_degree_9 float null,
	bef_degree_10 float null,
	bef_degree_11 float null,
	bef_degree_12 float null,
	constraint theme_hot_history_theme_code_uindex
		unique (theme_code)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

create table stocks.custom_theme
(
	id int auto_increment
		primary key,
	theme_code varchar(12) null,
	theme_name varchar(24) null,
	tmp_degree text null,
	bef_degree_1 float null,
	bef_degree_2 float null,
	bef_degree_3 float null,
	bef_degree_4 float null,
	bef_degree_5 float null,
	bef_degree_6 float null,
	bef_degree_7 float null,
	bef_degree_8 float null,
	bef_degree_9 float null,
	bef_degree_10 float null,
	bef_degree_11 float null,
	bef_degree_12 float null,
	constraint theme_hot_history_theme_code_uindex
		unique (theme_code)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;




