    # This returns liked works
    # works_list = db.session.query(WorkList, func.count(AlbumLike.id).label('total')) \
    #     .filter(WorkList.composer == name, WorkList.recommend == True)\
    #     .join(WorkAlbums, WorkAlbums.workid == WorkList.id)\
    #     .join(AlbumLike, AlbumLike.album_id == WorkAlbums.id)\
    #     .group_by(WorkAlbums)\
    #     .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    # This returns works with number of likes
    # works_list = db.session.query(WorkList, func.count(AlbumLike.id).label('total')) \
    #     .filter(WorkList.composer == name, WorkList.recommend == True)\
    #     .join(WorkAlbums, WorkAlbums.workid == WorkList.id)\
    #     .outerjoin(AlbumLike, AlbumLike.album_id == WorkAlbums.id)\
    #     .group_by(WorkList)\
    #     .order_by(WorkList.order, WorkList.genre, WorkList.id).all()

    # TESTING