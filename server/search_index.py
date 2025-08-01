from app import create_app
from app.models import ComposerList, WorkList, WorkAlbums
import logging
from tqdm import tqdm

# Suppress verbose transport logs
logging.getLogger("elastic_transport.transport").setLevel(logging.WARNING)

app = create_app()
app.app_context().push()

# Check ES connection
if not app.elasticsearch or not app.elasticsearch.ping():
    logging.error("Elasticsearch is not available. Exiting.")
    exit(1)


# Helper: wrap reindexing with a progress bar
def reindex_with_progress(model):
    objects = model.query.all()
    total = len(objects)
    for obj in tqdm(objects, desc=f"Indexing {model.__name__}", total=total):
        model.add_to_index(model.__tablename__, obj)


logging.info("Indexing composers...")
reindex_with_progress(ComposerList)

logging.info("Indexing works...")
reindex_with_progress(WorkList)

logging.info("Indexing albums...")
reindex_with_progress(WorkAlbums)

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
