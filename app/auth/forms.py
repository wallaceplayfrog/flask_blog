from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('输入旧密码', validators=[DataRequired()])
    password = PasswordField('输入新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码必须一致。')])
    password2 = PasswordField('再次输入新密码',
                              validators=[DataRequired()])
    submit = SubmitField('更改密码')


class RegistrationForm(FlaskForm):
    email = StringField('电子邮件地址', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名必须以字母开头，并且只能由字母数字下划线和小数点组成')])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册新用户')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')
    

class LoginForm(FlaskForm):
    email = StringField('电子邮箱地址', 
        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('登录')