from flask import render_template, request, url_for, flash, redirect
import datetime
from sqlalchemy import func
from app.models import ForumPost, Subforum, ForumComment, User
from flask_login import current_user, login_required
from app import db
from app.forum import bp


@bp.route('/forum')
def forum():
    # get statistics for posts and threads. Requires at least one thread in each forum.
    subforums = Subforum.query.order_by(Subforum.id).all()
    threads = db.session.query(func.count(ForumPost.id)).group_by(ForumPost.subforum_id).all()
    num_threads = [value for (value,) in threads]
    posts = db.session.query(func.count(ForumComment.id)).outerjoin(ForumPost).group_by(ForumPost.subforum_id).all()
    num_posts = [value for (value,) in posts]

    if current_user.is_authenticated:
        current_user.last_message_read_time = datetime.datetime.utcnow()
        db.session.commit()

    i = 0
    for subforum in subforums:
        try:
            subforum.num_threads = num_threads[i]
        except IndexError:
            subforum.num_threads = 0
        try:
            subforum.num_posts = num_posts[i] + num_threads[i]
        except IndexError:
            subforum.num_posts = 0
        subforum.last_post = db.session.query(ForumComment).join(ForumPost).filter(ForumPost.subforum_id == subforum.id).order_by(ForumComment.id.desc()).first()
        i += 1

    # icons for forums
    subforums[0].icon = "glyphicon glyphicon-music"
    subforums[1].icon = "glyphicon glyphicon-comment"
    subforums[2].icon = "glyphicon glyphicon-console"
    subforums[3].icon = "glyphicon glyphicon-bullhorn"
    subforums[4].icon = "glyphicon glyphicon-book"

    # get online users
    onlinecheck = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    users = db.session.query(User).filter(User.last_seen > onlinecheck).order_by(User.last_seen.desc()).all()

    return render_template("forum/subforums.html", users=users, subforums=subforums, title="Forum")


@bp.route('/subforum/<subforum_id>')
def subforum(subforum_id):

    if current_user.is_authenticated:
        current_user.last_message_read_time = datetime.datetime.utcnow()
        db.session.commit()

    page = int(request.args.get("page", 1))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first_or_404()
    posts = db.session.query(ForumPost).filter(
        ForumPost.subforum_id == subforum_id).order_by(
            ForumPost.last_comment_date.desc()).paginate(page, 20, False)

    # user viewing
    if current_user.is_authenticated:
        current_user.page_viewing = '<a href="' + url_for(
            "forum.subforum",
            subforum_id=subforum_id) + '">' + subforum.title + '</a>'
        db.session.commit()

    return render_template("forum/subforum.html",
                           subforum=subforum,
                           posts=posts,
                           title=subforum.title)


@ bp.route('/addpost')
@ login_required
def addpost():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first_or_404()
    return render_template("forum/createpost.html", subforum=subforum, title="Create Post")


@ bp.route('/viewpost/<post_id>')
def viewpost(post_id):
    if current_user.is_authenticated:
        current_user.last_message_read_time = datetime.datetime.utcnow()
        db.session.commit()
        
    page = int(request.args.get("page", 1))
    post = ForumPost.query.filter(ForumPost.id == post_id).first()
    if not post:
        abort(404)
    comments = ForumComment.query.filter(ForumComment.post_id == post_id).order_by(ForumComment.id).paginate(page, 20, False)

    if current_user.is_authenticated:
        current_user.view_post(post)
        current_user.page_viewing = '<a href="' + url_for("forum.viewpost", post_id=post_id) + '">' + post.title + '</a>'
        db.session.commit()

    return render_template("forum/viewpost.html", post=post, comments=comments, title=post.title)


@ bp.route('/action_comment', methods=['POST', 'GET'])
@ login_required
def comment():
    page = int(request.args.get("page", 1))
    post_id = int(request.args.get("post"))
    post = ForumPost.query.filter(ForumPost.id == post_id).first()
    if not post:
        flash("That post does not exist!", "danger")
        return redirect(url_for("forum.forum"))
    content = request.form['content']
    postdate = datetime.datetime.utcnow()
    comment = ForumComment(content, postdate)
    current_user.forum_comments.append(comment)
    post.last_commenter = current_user.display_name
    post.last_comment_username = current_user.username
    post.last_comment_date = datetime.datetime.utcnow()
    post.comments.append(comment)
    db.session.commit()
    flash("Your reply has been posted.", "info")
    return redirect("/viewpost/" + str(post_id) + "?page=" + str(page))


@ bp.route('/edit_post', methods=['POST', 'GET'])
@ login_required
def edit_post():
    page = int(request.args.get("page", 1))
    post_id = int(request.args.get("post"))
    post = ForumPost.query.filter(ForumPost.id == post_id).first()
    if not post:
        flash("That post does not exist!", "danger")
        return redirect(url_for("forum.forum"))

    content = request.form['content']

    if not current_user.id == post.user_id:
        flash("That is not your post to edit!", "danger")
        return redirect(url_for("forum.forum"))
    post.content = content

    db.session.commit()
    flash("Your post has been edited.", "info")
    return redirect("/viewpost/" + str(post_id))



@ bp.route('/edit_comment', methods=['POST', 'GET'])
@ login_required
def edit_comment():
    page = int(request.args.get("page", 1))
    post_id = int(request.args.get("post"))
    post = ForumPost.query.filter(ForumPost.id == post_id).first()
    if not post:
        flash("That post does not exist!", "danger")
        return redirect(url_for("forum.forum"))
    comment_id = request.form['comment_id']
    content = request.form['content']

    comment = ForumComment.query.filter(ForumComment.id == comment_id).first()
    if not comment:
        flash("That comment does not exist!", "danger")
        return redirect(url_for("forum.forum"))
    if not current_user.id == comment.user_id:
        flash("That is not your comment to edit!", "danger")
        return redirect(url_for("forum.forum"))
    comment.content = content
    db.session.commit()
    flash("Your comment has been edited.", "info")
    return redirect("/viewpost/" + str(post_id) + "?page=" + str(page))


@ bp.route('/action_post', methods=['POST'])
@ login_required
def action_post():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return redirect(url_for("forum.forum"))

    user = current_user
    title = request.form['title']
    content = request.form['content']

    post = ForumPost(title, content, datetime.datetime.utcnow())
    post.last_commenter = current_user.display_name
    post.last_comment_username = current_user.username
    post.last_comment_date = datetime.datetime.utcnow()
    subforum.posts.append(post)
    user.forum_posts.append(post)
    db.session.commit()
    flash("Your thread has been created.", "info")
    return redirect("/viewpost/" + str(post.id))


@ bp.route('/delete_forum_comment/<comment_id>')
@ login_required
def delete_forum_comment(comment_id):
    if not current_user.admin:
        return redirect(url_for("forum.forum"))

    comment = ForumComment.query.filter(ForumComment.id == comment_id).first()
    comment.post_id = 6
    db.session.commit()
    flash("Comment has been moved to orphanage.", "info")
    return redirect("/viewpost/6")


@ bp.route('/delete_forum_thread/<post_id>')
@ login_required
def delete_forum_thread(post_id):
    if not current_user.admin:
        return redirect(url_for("forum.forum"))

    post = ForumPost.query.filter(ForumPost.id == post_id).first()
    post.subforum_id = 10
    db.session.commit()
    flash("Post has been moved to archive.", "info")
    return redirect("/subforum/10")
