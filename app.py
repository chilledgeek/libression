import requests
from flask import Flask, render_template, Response
from flask_bootstrap import Bootstrap

from photo_organiser.file_organiser import FileOrganiser

app = Flask(__name__)
Bootstrap(app)


file_organiser = FileOrganiser()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html", buckets={"Name": "bla", "CreationDate": "bla"})


@app.route('/thumbnail/<path:key>')
def get_thumbnail(key):
    contents = file_organiser.load_from_cache(key)
    return Response(contents)


@app.route('/media/<path:key>')
def get_resource(key):
    response = requests.get(
        file_organiser.get_file_s3_url(key),
        stream=True,
    )
    return Response(response.raw, content_type=response.headers['content-type'])


@app.route('/view_files', methods=['GET', 'POST'])
def view_files():
    keys = file_organiser.list_objects()
    file_organiser.ensure_cache(keys)

    return render_template('view_files2.html', keys=keys)


if __name__ == "__main__":
    file_organiser.init_buckets()
    app.run()
