from app import create_app
from app.models import ComposerList, WorkList, WorkAlbums
import logging
from tqdm import tqdm
from elasticsearch import helpers

logging.getLogger("elastic_transport.transport").setLevel(logging.WARNING)

app = create_app()
app.app_context().push()

es = app.elasticsearch

# Check ES connection
if not es or not es.ping():
    logging.error("Elasticsearch is not available. Exiting.")
    exit(1)


# --- Helper: recreate index (delete & create fresh)
def recreate_index(index_name, searchable_fields):
    if es.indices.exists(index=index_name):
        logging.info(f"Deleting old index: {index_name}")
        es.indices.delete(index=index_name)
    # Simple mapping: all searchable fields as text
    mapping = {
        "mappings": {
            "properties": {field: {"type": "text"} for field in searchable_fields}
        }
    }
    logging.info(f"Creating new index: {index_name}")
    es.indices.create(index=index_name, body=mapping)


# --- Helper: bulk reindex with chunking
def bulk_reindex(model, chunk_size=1000):
    index_name = model.__tablename__
    searchable_fields = getattr(model, '__searchable__', [])
    recreate_index(index_name, searchable_fields)

    query = model.query.yield_per(chunk_size)  # stream in chunks
    total = model.query.count()

    def gen_actions():
        for obj in query:
            payload = {field: getattr(obj, field) for field in searchable_fields}
            yield {
                "_op_type": "index",
                "_index": index_name,
                "_id": obj.id,
                "_source": payload
            }

    logging.info(f"Indexing {total} {model.__name__} documents in chunks of {chunk_size}...")
    helpers.bulk(es, tqdm(gen_actions(), total=total, desc=f"Indexing {model.__name__}"), chunk_size=chunk_size)
    logging.info(f"{model.__name__} indexed successfully.")


# --- Run bulk indexing
logging.info("Rebuilding and indexing composers...")
bulk_reindex(ComposerList)

logging.info("Rebuilding and indexing works...")
bulk_reindex(WorkList)

logging.info("Rebuilding and indexing albums...")
bulk_reindex(WorkAlbums)

logging.info("Reindexing complete.")

# --- Interactive search
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
