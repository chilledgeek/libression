import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from photo_organiser.file_organiser import FileOrganiser

app = FastAPI()
file_organiser = FileOrganiser()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)


@app.get('/', response_class=RedirectResponse)
async def index() -> Response:
    url = app.url_path_for("render_navigation")
    return RedirectResponse(url=url)


@app.get('/thumbnail/{key:path}', response_class=StreamingResponse)
async def get_thumbnail(key: str) -> StreamingResponse:
    contents = file_organiser.load_from_cache(key)
    return StreamingResponse(contents)


@app.get('/media/{key:path}', response_class=StreamingResponse)
async def get_resource(key: str) -> StreamingResponse:
    s3_object = file_organiser.load_from_data_bucket(key)
    return StreamingResponse(content=s3_object["Body"], media_type=s3_object["ContentType"])


@app.get('/navigator/{rel_dir_no_slash:path}', response_class=HTMLResponse)
async def render_navigation_with_path(
        request: Request,
        rel_dir_no_slash: str,
        get_subdir_content: bool = False,
        show_hidden_content: bool = False,
) -> HTMLResponse:
    return await render_navigation(
        request=request,
        rel_dir_no_slash=rel_dir_no_slash,
        get_subdir_content=get_subdir_content,
        show_hidden_content=show_hidden_content,
    )


@app.get('/navigator', response_class=HTMLResponse)
async def render_navigation(
        request: Request,
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

    return templates.TemplateResponse(
        'navigator.html',
        {
            "request": request,
            "keys": file_keys,
            "nav_dirs": nav_dirs,
            "cur_dir": rel_dir_no_slash or ".",
        }
    )


if __name__ == "__main__":
    file_organiser.init_buckets()
    uvicorn.run(app, host="0.0.0.0", port=8000)




"""
# corresponding layout.html contents:

<html>
<head>
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.8/css/solid.css" integrity="sha384-v2Tw72dyUXeU3y4aM2Y0tBJQkGfplr39mxZqlTBDUZAb9BGoC40+rdFCG0m10lXk" crossorigin="anonymous">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.8/css/fontawesome.css" integrity="sha384-q3jl8XQu1OpdLgGFvNRnPdj5VIlCvgsDQTQB6owSOHWlAurxul7f+JpUOVdAiJ5P" crossorigin="anonymous">
  <link rel="stylesheet" href="/static/styles.css">
</head>

<title>Libression</title>

<div class="container">
  <div class="navbar">
    <ul class="nav navbar-nav">
      <li><a href="{{ url_for('render_navigation') }}">Top directory</a></li>
    </ul>
  </div>
</div>

<div class="container">{% block content %}{% endblock %}</div>


"""