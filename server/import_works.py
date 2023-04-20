import json
import os

from app import db
from app.models import WorkList
from app import create_app

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://composerexplorer:mrnisw269@localhost/composerexplorer'
app.app_context().push()

name = input("Enter short name of composer: ")

with open('../data/works/' + name + '.json') as f:
    worklist = json.load(f)

# delete existing works
#worklist = WorkList.query.filter_by(composer=name).delete()

# load new works
orders_entries = []
for orders in worklist:
    new_entry = WorkList(
        id=orders['id'],
        composer=orders['composer'],
        genre=orders['genre'],
        order=orders['order'],
        cat=orders['cat'],
        recommend=orders['recommend'],
        title=orders['title'],
        # search=orders['search'],
        date=orders['date'],
        openopus=False)
    db.session.merge(new_entry)
    orders_entries.append(new_entry)

db.session.commit()
print(orders_entries)