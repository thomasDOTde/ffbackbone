from flask import Blueprint

from flask import flash, redirect, session, url_for, request, g  # noqa
from flask.ext.login import login_user, logout_user, current_user, login_required  # noqa
from app.forms import *
from app.models import *
from app.email import *

session = Blueprint('session', __name__, template_folder='templates')



@session.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Contact.query.filter_by(login=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@session.route('/user/<login>')
@login_required
def user(login):
    user = Contact.query.filter_by(login=login).first_or_404()
    page = request.args.get('page', 1, type=int)
    return render_template('base.html')


@session.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@session.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = Contact.query.filter_by(mail=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.mail, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('login'))
    return render_template('auth/reset_password.html', form=form)


@session.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = Contact.query.filter_by(mail=form.email.data).first_or_404()
        if user is None:
            return redirect(url_for('index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('index'))
    return render_template('auth/reset_password.html', form=form)


@session.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
