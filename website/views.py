from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from flask_socketio import send
from flask_login import login_required, current_user
from .models import Post, Comment, User, FriendRequest
from .forms import AddPostForm, EditPostForm, AddCommentForm, EditCommentForm
from . import db, socketio

views = Blueprint('views', __name__)

@views.route('/', methods=['POST', 'GET'])
@login_required
def home():
    posts = Post.query.order_by(Post.id.desc()).all()
    users = User.query.order_by(User.id.desc()).all()
    friend_requests = FriendRequest.query.filter_by(is_active=True).all()
    return render_template('home.html', current_user=current_user, all_posts=posts, users=users, friend_requests=friend_requests )


@views.route('/userPosts', methods=['POST', 'GET'])
@login_required
def userPosts():
    return render_template('UserPosts.html', user=current_user)


@views.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@views.route('/post/<int:id>', methods=['POST', 'GET'])
@login_required
def post(id):
    post = Post.query.filter_by(id=id).one()
    form = AddCommentForm()
    return render_template('post.html', post=post, form=form)

# look up DELETE method
@views.route('/post/delete/<int:id>', methods=['POST','GET'])
@login_required
def deletePost(id):
    post = Post.query.get_or_404(id)
    if post.author == current_user.username:
        delete = Post.query.filter(Post.id==id).delete()
        db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/post/add', methods=['POST', 'GET'])
@login_required
def addPost():
    form = AddPostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, data=form.content.data, author=current_user.username, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit() 
        return redirect(url_for('views.home'))
    return render_template('addPost.html', form=form)

# look up PUT method
@views.route('/post/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def editPost(id):
    post = Post.query.get_or_404(id)
    form = EditPostForm()
    if post.author != current_user.username:
        return redirect(url_for('views.userPosts'))
    if form.validate_on_submit():
        post.title = form.title.data
        post.data = form.content.data
        db.session.commit()
        return redirect(url_for('views.userPosts'))
    form.title.data = post.title
    form.content.data = post.data

    return render_template('addPost.html', title='Edit Post', form=form)


@views.route('/post/<int:id>/comment/add', methods=['POST', 'GET'])
@login_required
def addComment(id):
    post = Post.query.get_or_404(id)
    form = AddCommentForm()
    if form.validate_on_submit():
        new_comment = Comment(username=current_user.username, data=form.commentField.data, post_id=id)
        db.session.add(new_comment)
        db.session.commit() 

        return redirect(url_for('views.post', id=id, form=form))  

    return render_template('post.html', post=post, form=form)


@views.route('/post/<int:post_id>/comment/delete/<int:comment_id>', methods=['POST', 'GET'])
@login_required
def deleteComment(comment_id, post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.filter_by(id=comment_id).first()
    form = AddCommentForm()
    if comment.username == current_user.username:
        delete = Comment.query.filter(Comment.id==comment_id).delete()
        db.session.commit()

    return redirect(url_for('views.post', id=post_id, form=form))  


@views.route('/post/<int:post_id>/comment/edit/<int:comment_id>', methods=['POST', 'GET'])
@login_required
def editComment(comment_id, post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.filter_by(id=comment_id).first()
    form = EditCommentForm()
    if comment.username != current_user.username:
        return redirect(url_for('views.post', id=post_id, form=form)) 
    if form.validate_on_submit():
        comment.data = form.commentField.data
        db.session.commit()
        return redirect(url_for('views.post', id=post_id, form=form)) 
    form.commentField.data = comment.data

    return render_template('post.html', post=post, form=form)


@views.route('/friend/add/<int:user_id>')
@login_required
def addfriend(user_id):
    user = User.query.filter_by(id=user_id).first()
    friend_request = FriendRequest.query.filter_by(sender=user.id, receiver=current_user.id).first()
    if user is None:
        return redirect(url_for('views.home'))
    if user == current_user:
        return redirect(url_for('views.home'))
    u = friend_request.accept()
    if u is None:
        return redirect(url_for('views.home'))
    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/friend/remove/<int:user_id>')
@login_required
def removefriend(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return redirect(url_for('views.home'))
    if user == current_user:
        return redirect(url_for('views.home'))
    u = current_user.remove_friend(user)
    if u is None:
        return redirect(url_for('views.home'))
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('friends/request/<int:user_id>/<request>', methods=['POST','GET'])
@login_required
def sendFriendRequest(user_id, request):
    user = User.query.filter_by(id=user_id).first()
    friend_request = FriendRequest.query.filter_by(sender=current_user.id, receiver=user.id).first()
    if user == current_user:
        return redirect(url_for('views.home'))
    if request == 'False':
        friend_request = FriendRequest.query.filter_by(sender=user.id, receiver=current_user.id).first()
        friend_request.decline()
        db.session.commit()
        return redirect(url_for('views.home'))
    if user is None:
        return redirect(url_for('views.home'))
    if friend_request:
        friend_request.is_active = True
        db.session.commit()
        return redirect(url_for('views.home'))
    new_friend_request = FriendRequest(sender=current_user.id, receiver=user.id)
    db.session.add(new_friend_request)
    db.session.commit()
        
    return redirect(url_for('views.home'))

