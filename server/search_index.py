from app import create_app
from app.models import ComposerList, WorkList, WorkAlbums
import logging
from tqdm import tqdm
from elasticsearch import helpers

# Suppress verbose ES HTTP logs
logging.getLogger("elastic_transport.transport").setLevel(logging.WARNING)

app = create_app()
app.app_context().push()

es = app.elasticsearch

# Check ES connection
if not es or not es.ping():
    logging.error("Elasticsearch is not available. Exiting.")
    exit(1)


# Helper: bulk reindex with progress
def bulk_reindex(model):
    objects = model.query.all()
    total = len(objects)

    actions = []
    for obj in tqdm(objects, desc=f"Preparing {model.__name__} for indexing", total=total):
        payload = {field: getattr(obj, field) for field in getattr(model, '__searchable__', [])}
        actions.append({
            "_op_type": "index",
            "_index": model.__tablename__,
            "_id": obj.id,
            "_source": payload
        })

    logging.info(f"Indexing {total} {model.__name__} documents...")
    helpers.bulk(es, actions)
    logging.info(f"{model.__name__} indexed successfully.")


logging.info("Bulk indexing composers...")
bulk_reindex(ComposerList)

logging.info("Bulk indexing works...")
bulk_reindex(WorkList)

logging.info("Bulk indexing albums...")
bulk_reindex(WorkAlbums)

logging.info("Reindexing complete.")

# Interactive search
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
        results, total = model.elasticsearch(q, 1, 10 if label == "Composers" else 1000, sort)
        print(f"{label} ({total} results): {results[:10]}")
        print()
