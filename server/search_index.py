from app import create_app
from app.models import ComposerList, WorkList, WorkAlbums
import logging

logging.basicConfig(level=logging.INFO)

app = create_app()
app.app_context().push()

# Check ES connection
if not app.elasticsearch or not app.elasticsearch.ping():
    logging.error("Elasticsearch is not available. Exiting.")
    exit(1)

logging.info("Indexing composers...")
ComposerList.reindex()
logging.info("Indexing works...")
WorkList.reindex()
logging.info("Indexing albums...")
WorkAlbums.reindex()
logging.info("Reindexing complete.")

while True:
    q = input("Enter search term (or 'q' to quit): ")
    if q.lower() in ('q', 'quit', 'exit'):
        break

    logging.info("Searching...")
    for label, model, sort in [
        ("Composers", ComposerList, None),
        ("Works", WorkList, 'album_count'),
        ("Albums", WorkAlbums, 'score')
    ]:
        query, total = model.elasticsearch(q, 1, 10 if label == "Composers" else 1000, sort)
        print(f"{label} ({total} results): {query.limit(10).all()}")
        print()
