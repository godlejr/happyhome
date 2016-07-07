CREATE TABLE `files` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '일련번호',
	`type` INT(11) NOT NULL DEFAULT '1' COMMENT '파일형식(1:사진, 2:360사진, 3:동영상)',
	`name` VARCHAR(255) NOT NULL COMMENT '파일이름' COLLATE 'utf8mb4_unicode_ci',
	`ext` VARCHAR(255) NOT NULL COMMENT '파일확장자' COLLATE 'utf8mb4_unicode_ci',
	`size` INT(11) NOT NULL COMMENT '파일크기',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록일시',
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수정일시',
	PRIMARY KEY (`id`)
)
COMMENT='파일정보'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;
