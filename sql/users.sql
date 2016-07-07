CREATE TABLE `users` (
	`id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '일련번호',
	`email` VARCHAR(100) NOT NULL COMMENT 'Email(사용자 ID로 사용)' COLLATE 'utf8mb4_unicode_ci',
	`password` VARCHAR(255) NOT NULL COMMENT '암호화된 사용자 패스워드' COLLATE 'utf8mb4_unicode_ci',
	`name` VARCHAR(255) NOT NULL COMMENT '사용자 이름' COLLATE 'utf8mb4_unicode_ci',
	`level` INT(11) NOT NULL DEFAULT '0' COMMENT '사용자 레벨(0:사용자, 9:관리자)',
	`authenticated` TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Email 인증 여부(FALSE:0, TRUE:1)',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록일시',
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수정일시',
	`accesscode` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `users_idx01` (`email`)
)
COMMENT='사용자 계정 정보'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;
