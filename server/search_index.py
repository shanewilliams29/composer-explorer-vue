from test_secrets import os
from app import create_app
from app.models import ComposerList, WorkList, WorkAlbums, Performers

app = create_app()
app.app_context().push()

print(app.elasticsearch)

print("Indexing composers...")
ComposerList.reindex()
print("Done!")
print("Indexing works...")
WorkList.reindex()
print("Done!")
print("Indexing works...")
WorkAlbums.reindex()
print("Done!")

# while True:
#     q = input("Enter search term: ")

#     print("Composers:")
#     query, total = ComposerList.elasticsearch(q, 1, 10)
#     print(total)
#     print(query.limit(10).all())
#     print(" ")
#     print("Works:")
#     query, total = WorkList.elasticsearch(q, 1, 1000, 'album_count')
#     print(total)
#     print(query.limit(10).all())
#     print(" ")
#     print("Performers:")
#     query, total = Performers.elasticsearch(q, 1, 100)
#     print(total)
#     print(query.limit(10).all())
#     print(" ")
#     print("Albums:")
#     query, total = WorkAlbums.elasticsearch(q, 1, 1000, 'score')
#     print(total)
#     print(query.limit(10).all())
#     print(" ")
