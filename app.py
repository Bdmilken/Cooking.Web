import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import inspect, text

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'videos')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'


db = SQLAlchemy(app)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    likes = db.Column(db.Integer, default=0)

    comments = db.relationship('Comment', backref='video', cascade='all, delete-orphan')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('video')]
    if 'description' not in columns:
        db.session.execute(text("ALTER TABLE video ADD COLUMN description TEXT DEFAULT ''"))
        db.session.commit()


@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)


@app.post('/like/<int:video_id>')
def like(video_id):
    video = Video.query.get_or_404(video_id)
    liked = session.get('liked_videos', [])
    if video_id in liked:
        if video.likes > 0:
            video.likes -= 1
        liked.remove(video_id)
    else:
        video.likes += 1
        liked.append(video_id)
    session['liked_videos'] = liked
    db.session.commit()
    return redirect(url_for('index'))


@app.post('/comment/<int:video_id>')
def comment(video_id):
    video = Video.query.get_or_404(video_id)
    content = request.form['content']
    if content.strip():
        db.session.add(Comment(video=video, content=content.strip()))
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password != os.environ.get('PRODUCER_PASSWORD', 'Peachiesbbiesrock1456'):
            return 'Unauthorized', 403
        file = request.files.get('video')
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        if not file or not title:
            return 'Title and video required', 400
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        db.session.add(Video(filename=filename, title=title, description=description))
        db.session.commit()
        return redirect(url_for('index'))
    videos = Video.query.all()
    return render_template('upload.html', videos=videos)


@app.post('/delete/<int:video_id>')
def delete(video_id):
    password = request.form.get('password', '')
    if password != os.environ.get('PRODUCER_PASSWORD', 'Peachiesbbiesrock1456'):
        return 'Unauthorized', 403
    video = Video.query.get_or_404(video_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('upload'))


@app.post('/edit/<int:video_id>')
def edit(video_id):
    password = request.form.get('password', '')
    if password != os.environ.get('PRODUCER_PASSWORD', 'Peachiesbbiesrock1456'):
        return 'Unauthorized', 403
    video = Video.query.get_or_404(video_id)
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    if title:
        video.title = title
    video.description = description
    db.session.commit()
    return redirect(url_for('upload'))


if __name__ == '__main__':
    app.run(debug=True)
