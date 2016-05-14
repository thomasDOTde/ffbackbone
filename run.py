#!/usr/bin/env python
from app import app
from app.models import TunnelType
from app.models import db

# Initialize Database with defaults
if TunnelType.query.filter_by(id=1).first() is None:
    gre = TunnelType(id=1, name='GRE')
    db.session.add(gre)
    db.session.commit()

app.run(debug=True, host='0.0.0.0')
