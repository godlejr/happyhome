CREATE   TABLE  users
(        id             INT               NOT NULL AUTO_INCREMENT COMMENT '일련번호'
,        email          VARCHAR  ( 100)   NOT NULL COMMENT 'Email(사용자 ID로 사용)'
,        password       VARCHAR  ( 255)   NOT NULL COMMENT '암호화된 사용자 패스워드'
,        level          INT               NOT NULL DEFAULT '0' COMMENT '사용자 레벨(0:사용자, 9:관리자)'
,        authenticated  BOOLEAN           NOT NULL DEFAULT FALSE COMMENT 'Email 인증 여부(FALSE:0, TRUE:1)'
,        created_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록일시'
,        updated_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수정일시'
,        PRIMARY KEY (id)
,        UNIQUE KEY users_idx01(email)
) COMMENT='계정정보';
