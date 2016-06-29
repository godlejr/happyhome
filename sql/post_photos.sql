CREATE TABLE `snapshot_photos` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '일련번호',
	`snapshot_id` INT(11) NOT NULL COMMENT '스냅샷ID',
	`photo_id` INT(11) NOT NULL COMMENT '사진ID',
	PRIMARY KEY (`id`)
)