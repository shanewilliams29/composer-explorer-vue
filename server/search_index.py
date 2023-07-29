from test_secrets import os
from app import create_app
from app.models import ComposerList, WorkList, WorkAlbums

app = create_app()
app.app_context().push()

print(app.elasticsearch)

# WorkAlbums.reindex()
q = input("Enter search term: ")

print("Composers:")
query, total = ComposerList.elasticsearch(q, 1, 10)
print(total)
print(query.all())
print(" ")
print("Works:")
query, total = WorkList.elasticsearch(q, 1, 10)
print(total)
print(query.all())
print(" ")
print("Albums ")
query, total = WorkAlbums.elasticsearch(q, 1, 10)
print(total)
print(query.all())
print(" ")
