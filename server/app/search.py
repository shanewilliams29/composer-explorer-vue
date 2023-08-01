from flask import current_app
from unidecode import unidecode

# def add_to_index(index, model):
#     if not current_app.elasticsearch:
#         return
#     payload = {}
#     for field in model.__searchable__:
#         payload[field] = getattr(model, field)
#     current_app.elasticsearch.index(index=index, id=model.id, body=payload)

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        value = getattr(model, field)
        # Convert the value to lowercase and remove accents
        if value:
            value = unidecode(value.lower())
        payload[field] = value
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch or not query.strip():
        return [], 0
    search = current_app.elasticsearch.search(index=index,
                                              body={
                                                  'query': {
                                                      'multi_match': {
                                                          'query': query,
                                                          'fields': ['*'],
                                                          'type': 'cross_fields'
                                                      }
                                                  },
                                                  'from': (page - 1) * per_page,
                                                  'size': per_page
                                              })
    ids = [hit['_id'] for hit in search['hits']['hits']]
    scores = [hit['_score'] for hit in search['hits']['hits']]

    return ids, scores, search['hits']['total']['value']


# def query_index(index, query, page, per_page):
#     if not current_app.elasticsearch:
#         return [], 0
#     query_parts = query.split()
#     if len(query_parts) == 2:
#         search = current_app.elasticsearch.search(
#             index=index,
#             body={'query': {
#                       'bool': {
#                           'should': [
#                               {
#                                   'match': {
#                                       'composer': {
#                                           'query': query_parts[0],
#                                           'boost': 3
#                                       }
#                                   }
#                               },
#                               {
#                                   'match': {
#                                       'title': {
#                                           'query': query_parts[1],
#                                           'boost': 2
#                                       }
#                                   }
#                               }
#                           ]
#                       }},
#               'from': (page - 1) * per_page, 'size': per_page})
#     else:
#         search = current_app.elasticsearch.search(
#             index=index,
#             body={'query': {
#                       'multi_match': {
#                           'query': query,
#                           'fields': ['composer^3', 'title^2', '*'],
#                           'type': 'best_fields'
#                       }},
#                   'from': (page - 1) * per_page, 'size': per_page})
#     ids = [hit['_id'] for hit in search['hits']['hits']]
#     return ids, search['hits']['total']['value']