from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask_login import login_user, login_required, logout_user
from ..models import User
from .forms import LoginForm 

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remeber_me.data)
            next = request.args.get('next')
            if next is None or not next.startwith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('错误的用户名或密码')
    return render_template('auth/login.html', form = form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('登出完成')
    return redirect(url_for('mian.index'))