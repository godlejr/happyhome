from flask import current_app, session, render_template
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib import sqla
from flask_login import current_user
from happyathome import User
from happyathome.models import Category, Magazine, Photo, Comment, Board, Residence, Business, Room, db


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if not session.get('user_id'):
            return False
        return current_user.is_admin

    @expose('/')
    def index(self):
        join_yearly_users = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as user_count
                    from 	users
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    and     level<>9
                    GROUP BY month(created_at)
            ''')

        yearly_users = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as user_count
                    from 	users
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    and     level<>9
                    GROUP BY month(created_at)
            ''')

        temp_yearly_users = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as user_count
                    from 	users
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    and     level<>9
                    GROUP BY month(created_at)
            ''')

        join_monthly_users = db.session.execute('''
        select  substring(created_at,1,4) as year,
                substring(created_at,6,2) as month,
                substring(created_at,9,2) as day,
                substring(created_at,1,10) as date,
                count(*)  as user_count
                from 	users
                WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                and     level<>9
                GROUP BY WEEK(created_at)
        ''')

        monthly_users = db.session.execute('''
        select  substring(created_at,1,4) as year,
                substring(created_at,6,2) as month,
                substring(created_at,9,2) as day,
                substring(created_at,1,10) as date,
                count(*)  as user_count
                from 	users
                WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                and     level<>9
                GROUP BY WEEK(created_at)
        ''')

        temp_monthly_users = db.session.execute('''
        select  substring(created_at,1,4) as year,
                substring(created_at,6,2) as month,
                substring(created_at,9,2) as day,
                substring(created_at,1,10) as date,
                count(*)  as user_count
                from 	users
                WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                and     level<>9
                GROUP BY WEEK(created_at)
        ''')

        join_daily_users = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as user_count
                    from 	users
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    and     level<>9
                    group by date
        ''')

        daily_users = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as user_count
                    from 	users
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    and     level<>9
                    group by date
        ''')

        temp_daily_users = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as user_count
                    from 	users
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    and     level<>9
                    group by date
        ''')

        user_count = User.query.filter_by(level=1).count()
        pro_count = User.query.filter_by(level=2).count()

        minus_daily_user = []
        for temp_user in temp_daily_users:
            minus_daily_user.append((pro_count + user_count) - temp_user.user_count)
            minus_daily_user.pop(0)
            minus_daily_user.append(pro_count + user_count)

        minus_monthly_user = []
        for temp_user in temp_monthly_users:
            minus_monthly_user.append((pro_count + user_count) - temp_user.user_count)
            minus_monthly_user.pop(0)
            minus_monthly_user.append(pro_count + user_count)

        minus_yearly_user = []
        for temp_user in temp_yearly_users:
            minus_yearly_user.append((pro_count + user_count) - temp_user.user_count)
            minus_yearly_user.pop(0)
            minus_yearly_user.append(pro_count + user_count)

        join_daily_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    group by date
        ''')

        daily_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    group by date
        ''')

        temp_daily_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    group by date
        ''')

        join_monthly_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                    GROUP BY WEEK(created_at)
        ''')

        monthly_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                    GROUP BY WEEK(created_at)
        ''')

        temp_monthly_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                    GROUP BY WEEK(created_at)
        ''')

        join_yearly_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    GROUP BY month(created_at)
        ''')

        yearly_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    GROUP BY month(created_at)
        ''')

        temp_yearly_stories = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as story_count
                    from 	magazines
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    GROUP BY month(created_at)
        ''')

        rooms = Room.query
        categories = Category.query

        categories_sum = 0
        for category in categories.all():
            categories_sum += Magazine.query.filter(Magazine.category_id == category.id).count()
        categories = categories.all()

        join_daily_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    group by date
        ''')

        daily_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    group by date
        ''')

        temp_daily_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) < 7
                    group by date
        ''')

        join_monthly_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                    GROUP BY WEEK(created_at)
        ''')

        monthly_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                    GROUP BY WEEK(created_at)
        ''')

        temp_monthly_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 31
                    GROUP BY WEEK(created_at)
        ''')

        join_yearly_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    GROUP BY month(created_at)
        ''')

        yearly_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    GROUP BY month(created_at)
        ''')

        temp_yearly_galleries = db.session.execute('''
            select  substring(created_at,1,4) as year,
                    substring(created_at,6,2) as month,
                    substring(created_at,9,2) as day,
                    substring(created_at,1,10) as date,
                    count(*)  as gallery_count
                    from 	photos
                    WHERE 	TO_DAYS(NOW()) - TO_DAYS(created_at) <= 365
                    GROUP BY month(created_at)
        ''')

        rooms_sum = 0
        for room in rooms.all():
            rooms_sum += Photo.query.filter(Photo.room_id == room.id).count()
        rooms = rooms.all()

        minus_daily_story = []
        for temp_story in temp_daily_stories:
            minus_daily_story.append( categories_sum - temp_story.story_count)
            minus_daily_story.pop(0)
            minus_daily_story.append( categories_sum )

        minus_monthly_story = []
        for temp_story in temp_monthly_stories:
            minus_monthly_story.append(categories_sum - temp_story.story_count)
            minus_monthly_story.pop(0)
            minus_monthly_story.append(categories_sum)

        minus_yearly_story = []
        for temp_story in temp_yearly_stories:
            minus_yearly_story.append(categories_sum - temp_story.story_count)
            minus_yearly_story.pop(0)
            minus_yearly_story.append(categories_sum)

        minus_daily_gallery = []
        for temp_gallery in temp_daily_galleries:
            minus_daily_gallery.append(rooms_sum - temp_gallery.gallery_count)
            minus_daily_gallery.pop(0)
            minus_daily_gallery.append(rooms_sum)

        minus_monthly_gallery = []
        for temp_gallery in temp_monthly_galleries:
            minus_monthly_gallery.append(rooms_sum - temp_gallery.gallery_count)
            minus_monthly_gallery.pop(0)
            minus_monthly_gallery.append(rooms_sum)

        minus_yearly_gallery = []
        for temp_gallery in temp_yearly_galleries:
            minus_yearly_gallery.append(rooms_sum - temp_gallery.gallery_count)
            minus_yearly_gallery.pop(0)
            minus_yearly_gallery.append(rooms_sum)

        pro_story_count = Magazine.query.join(User).filter(User.level == 2).count()
        pro_gallery_count = Photo.query.join(User).filter(User.level == 2).count()

        board_total =  Board.query.count()
        board_question_total = Board.query.filter(Board.depth == 0).count()
        board_answer_total = Board.query.filter(Board.depth == 1 ).count()
        return self.render(current_app.config['TEMPLATE_THEME'] + '/admin/index.html',
                           rooms=rooms, user_count=user_count, pro_count=pro_count, pro_story_count=pro_story_count,
                           board_total=board_total, rooms_sum=rooms_sum, categories_sum=categories_sum,
                           pro_gallery_count=pro_gallery_count, board_question_total=board_question_total,
                           board_answer_total=board_answer_total, daily_users=daily_users,
                           minus_daily_user=minus_daily_user,
                           join_daily_users=join_daily_users,
                           monthly_users=monthly_users, join_monthly_users=join_monthly_users,
                           minus_monthly_user=minus_monthly_user,
                           minus_yearly_user=minus_yearly_user, join_yearly_users=join_yearly_users,
                           yearly_users=yearly_users, minus_daily_story=minus_daily_story,
                           join_daily_stories=join_daily_stories, daily_stories=daily_stories,
                           join_monthly_stories=join_monthly_stories, monthly_stories=monthly_stories,
                           minus_monthly_story=minus_monthly_story,yearly_stories=yearly_stories,join_yearly_stories=join_yearly_stories,
                           minus_yearly_story=minus_yearly_story,
                           minus_daily_gallery=minus_daily_gallery,minus_monthly_gallery=minus_monthly_gallery,minus_yearly_gallery=minus_yearly_gallery,
                           join_daily_galleries=join_daily_galleries,join_monthly_galleries=join_monthly_galleries,join_yearly_galleries=join_yearly_galleries,
                           daily_galleries=daily_galleries,monthly_galleries=monthly_galleries,yearly_galleries=yearly_galleries,
                           categories=categories)


# admin class
class UserAdmin(sqla.ModelView):
    column_display_pk = True
    # Disable model creation

    # Override displayed fields
    column_list = ('id', 'name', 'email', 'authenticated', 'accesscode')  # column 이름변견
    form_columns = ['name', 'email', 'authenticated', 'accesscode']  # form 변경사항 저장
    column_searchable_list = ('name', 'email', 'authenticated', 'accesscode')  # 검색 기준설정

    # change field name
    column_labels = dict(id='No', name='이름', email='이메일', authenticated='인증', accesscode='소셜아이디')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminCategory(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('name',)
    form_columns = ('name',)
    column_searchable_list = (Category.id, Category.name)
    column_labels = dict(name='테마 이름')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminResidence(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('name',)
    form_columns = ('name',)
    column_searchable_list = (Residence.id, Residence.name)
    column_labels = dict(name='장소 이름')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminBusiness(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('name',)
    form_columns = ('name',)
    column_searchable_list = (Business.id, Business.name)
    column_labels = dict(name='업종 이름')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminPhoto(sqla.ModelView):
    column_display_pk = True

    # Override displayed fields
    column_list = ('user', 'file', 'content', 'hits')
    form_columns = ('user', 'file', 'content', 'hits', 'magazine')
    column_searchable_list = (User.name, User.email, Photo.content)
    column_labels = dict(user='사용자', file='파일', content='내용', hits='조회수', magazine='매거진')

    def is_accessible(self):
        return current_user.is_admin


class ClassAdminMagazine(sqla.ModelView):
    column_display_pk = True

    column_list = ('user', 'category', 'title', 'content', 'hits')
    form_columns = ['user', 'category', 'title', 'content', 'hits', 'photos']
    column_searchable_list = (User.name, User.email, Category.name, Magazine.title, Magazine.content)

    column_labels = dict(user='사용자', category='범주', title='제목', content='내용', hits='조회수', photos='사진들')

    def is_accessible(self):
        return current_user.is_admin


class CommentAdminFile(sqla.ModelView):
    column_display_pk = True
    column_list = ('user', 'content')
    form_columns = ['user', 'content']
    column_searchable_list = (User.name, User.email, Comment.content)

    column_labels = dict(user='사용자', content='내용')

    def is_accessible(self):
        return current_user.is_admin


class BoardAdminFile(sqla.ModelView):
    column_display_pk = True

    column_list = ('user', 'content')
    form_columns = ['user', 'content']
    column_searchable_list = (User.name, User.email, Board.content)

    column_labels = dict(user='사용자', content='내용')

    def is_accessible(self):
        return current_user.is_admin

