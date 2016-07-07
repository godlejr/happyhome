CREATE TABLE `magazine_photos` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '순번',
	`magazine_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'MagazineID',
	`photo_id` INT(11) NOT NULL DEFAULT '0' COMMENT 'PhotoID',
	PRIMARY KEY (`id`)
)
COMMENT='매거진-포토 연결고리'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;
