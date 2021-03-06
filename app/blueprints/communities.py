from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request, g  # noqa
from flask.ext.login import current_user, login_required
from datetime import datetime
from app.forms import *
from app.models import *

communities = Blueprint('communities', __name__, template_folder='templates')

@communities.route('/community')
@communities.route('/community/')
@login_required
def list():
    communities_self = Community.query.join(
        Contact,
        Community.contacts
    ).options(db.joinedload('asns')).options(
        db.lazyload('nameservers')
    ).filter_by(id=current_user.id).options(
        db.joinedload('contacts')).all()
    return render_template('community/list.html',
                           communities=communities_self)


@communities.route('/community/<community_id>', methods=['GET', 'POST'])
@login_required
def edit(community_id):
    this_community=Community.query.filter_by(id=community_id).first()
    form = FormCommunity(obj=this_community)
    form.submit.label.text='Update Community'
    if form.validate_on_submit():
        form.populate_obj(this_community)
        db.session.add(this_community)
        this_community.created = datetime.now()
        db.session.commit()
        return redirect(url_for('communities.list'))
    return render_template('community/detail.html',
                           form=form, edit=True)


@communities.route('/community/new', methods=['GET', 'POST'])
@login_required
def create():
    this_community=Community()
    form = FormCommunity()
    form.submit.label.text='Create Community'
    if form.validate_on_submit():
        form.populate_obj(this_community)
        db.session.add(this_community)
        this_community.contacts.append(current_user)
        db.session.commit()
        return redirect(url_for('communities.list'))
    return render_template('community/detail.html',
                           form=form, edit=False)

