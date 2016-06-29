CREATE TABLE `magazine_photos` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '일련번호',
	`magazine_id` INT(11) NOT NULL COMMENT '매거진ID',
	`photo_id` INT(11) NOT NULL COMMENT '사진ID',
	PRIMARY KEY (`id`)
)