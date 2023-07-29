from test_secrets import os
from app import create_app
from app.models import ComposerList, WorkList, WorkAlbums

app = create_app()
app.app_context().push()

print(app.elasticsearch)

# WorkAlbums.reindex()

query, total = WorkList.elasticsearch("Wagner Tristan", 1, 10)
print(total)
print(query.all())
