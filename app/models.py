from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from markdown import markdown
import bleach


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target, value, old_value, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


# 定义Role和User模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)  # 只有一个角色可以为True 
    '''
    关注用户：1 FOLLOW 
    在他人的文章中发表评论：2 COMMENT
    写文章：4 WRITE
    管理他人评论：8 MODERATE 
    管理员权限：16 ADMIN
    ''' 
    permissions = db.Column(db.Integer) 
    # 代表这个关系的面向对象视角， 返回与角色关联的用户组成的列表
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                            Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                                Permission.WRITE, Permission.MODERATE,
                                Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
            db.session.commit()


    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm
    
    def reset_permissions(self):
        self.permissions = 0
    
    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 建立外键
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 在User模型中加入密码散列
    password_hash = db.Column(db.String(128))
    # 确认用户账户
    confirmed = db.Column(db.Boolean, default=False)
    # 新增用户信息字段
    name = db.Column(db.String(64))  # 真实姓名
    location = db.Column(db.String(64))  # 所在地
    about_me = db.Column(db.Text())  # 自我介绍
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 注册日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 最后访问日期
    posts = db.relationship('Post', backref='author', lazy='dynamic')  # 发帖外键

    def ping(self):  # 刷新用户的最后访问时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    
    # 检验用户是否有指定的权限
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')
    
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


# 游客
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))