import logging

from flask import Flask, render_template, Response, redirect
from flask_bootstrap import Bootstrap

from photo_organiser.file_organiser import FileOrganiser

app = Flask(__name__)
Bootstrap(app)

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)

file_organiser = FileOrganiser()


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect("/navigator")


@app.route('/thumbnail/<path:key>')
def get_thumbnail(key):
    contents = file_organiser.load_from_cache(key)
    return Response(contents)


@app.route('/media/<path:key>')
def get_resource(key):
    s3_object = file_organiser.load_from_data_bucket(key)
    return Response(s3_object["Body"], mimetype=s3_object["ContentType"])


@app.route('/navigator/<path:rel_dir_no_slash>')
def render_navigation_with_path(
        rel_dir_no_slash: str,
        get_subdir_content: bool = False,
        show_hidden_content: bool = False,
):
    return render_navigation(
        rel_dir_no_slash=rel_dir_no_slash,
        get_subdir_content=get_subdir_content,
        show_hidden_content=show_hidden_content,
    )


@app.route('/navigator', methods=['GET', 'POST'], strict_slashes=False)
def render_navigation(
        rel_dir_no_slash: str = "",
        get_subdir_content: bool = False,
        show_hidden_content: bool = False,
):
    nav_dirs, file_keys = file_organiser.get_rel_dirs_and_content(
        rel_dir_no_slash=rel_dir_no_slash,
        get_subdir_content=get_subdir_content,
        show_hidden_content=show_hidden_content,
    )

    file_organiser.ensure_cache_bulk(file_keys)

    return render_template(
        'navigator.html',
        keys=file_keys,
        nav_dirs=nav_dirs,
        cur_dir=rel_dir_no_slash or "."
    )


if __name__ == "__main__":
    file_organiser.init_buckets()
    app.run()
