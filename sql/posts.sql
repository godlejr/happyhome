CREATE   TABLE  posts
(        id             INT               NOT NULL AUTO_INCREMENT COMMENT '일련번호'
,        user_id        INT               NOT NULL COMMENT '사용자ID'
,        title          VARCHAR  ( 255)   NOT NULL COMMENT '제목'
,        content        TEXT              NOT NULL COMMENT '내용'
,        created_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록일시'
,        updated_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수정일시'
,        PRIMARY KEY (id)
) COMMENT='포스트내역';

