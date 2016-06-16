CREATE   TABLE  photos
(        id             INT               NOT NULL AUTO_INCREMENT COMMENT '일련번호'
,        post_id        INT               NOT NULL COMMENT '포스트ID'
,        filename       VARCHAR  ( 255)   NOT NULL COMMENT '파일이름'
,        filesize       INT               NOT NULL COMMENT '파일크기'
,        created_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록일시'
,        updated_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수정일시'
,        PRIMARY KEY (id)
) COMMENT='포스트내역';
