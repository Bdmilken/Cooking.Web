import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

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
    likes = db.Column(db.Integer, default=0)

    comments = db.relationship('Comment', backref='video', cascade='all, delete-orphan')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)


@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)


@app.post('/like/<int:video_id>')
def like(video_id):
    video = Video.query.get_or_404(video_id)
    video.likes += 1
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
        if password != os.environ.get('PRODUCER_PASSWORD', 'secret'):
            return 'Unauthorized', 403
        file = request.files.get('video')
        title = request.form.get('title', '')
        if not file or not title:
            return 'Title and video required', 400
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        db.session.add(Video(filename=filename, title=title))
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('upload.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
