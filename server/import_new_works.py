import json
from test_secrets import os

from app import db
from app.models import WorkList
from app import create_app

app = create_app()
app.app_context().push()

name = input("Enter short name of composer: ")

with open('../data/works/' + name + '.json') as f:
    worklist = json.load(f)

# load new works
entries = []
for work in worklist:
    new_entry = WorkList(
        id=work['id'],
        composer=work['composer'],
        genre=work['genre'],
        order=work['order'],
        cat=work['cat'],
        recommend=work['recommend'],
        nickname=work['nickname'],
        title=work['title'],
        date=work['date']
        )
    db.session.merge(new_entry)
    entries.append(new_entry)

db.session.commit()
print(entries)
