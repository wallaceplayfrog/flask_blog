from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from flask_pagedown.fields import PageDownField


# 定义表单类
# 包含一个文本字段和一个提交按钮
class NameForm(FlaskForm):
    name = StringField('what is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# 资料编辑表单
class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('提交')


# 管理员级编辑资料表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$', 0, '用户名必须以字母开头，并且只能由字母数字下划线和小数点组成')])
    confirmed = BooleanField('账户确认')
    role = SelectField('用户权限', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) 
                            for role in Role.query.order_by(Role.name).all()]
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.eamil and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经存在')
    
    def validate_username(self, field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在')


class PostForm(FlaskForm):
    body = PageDownField('有点想法？', validators=[DataRequired()])
    sbumit = SubmitField('提交')
