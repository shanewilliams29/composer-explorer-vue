from flask import json

from app.models import ComposerList, Artists
from app import create_app, db
app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://old:vJ6eA8nQ6aY8tU9oT2hW8kV8pD3vZ9sK@34.66.133.61/composerexplorer'
app.app_context().push()

composers = ComposerList.query.filter_by(catalogued=True).order_by(ComposerList.name_short).all()

composer_list = []
for index, composer in enumerate(composers):

    composer_list.append(composer.name_short)

    artists = db.session.query(Artists.name).filter(Artists.composer == composer.name_short)\
        .order_by(Artists.name).distinct().all()

    artist_list = []
    for (artist, ) in artists:
        artist_list.append(artist)

    with open(f"../data/network/{composer.name_short}.json", 'w', encoding='utf8') as outfile:
        json.dump(artist_list, outfile, ensure_ascii=False)

    print(f"Completed {composer.name_short}! {index + 1} of {len(composers)} complete.")

with open("../data/network/composer_list.json", 'w', encoding='utf8') as outfile:
    json.dump(composer_list, outfile, ensure_ascii=False)

print("Completed export of composers!")
