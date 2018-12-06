# BindSympli

BindSympli is a tool to download design layout images from [Sympli](https://sympli.io/) CDN using certain Sympli account, to resize these images, and to bind them with the documentation project.

## Installation

Before using BindSympli, you need to install [Node.js](https://nodejs.org/en/), [Puppeteer](https://github.com/GoogleChrome/puppeteer), [wget](https://www.gnu.org/software/wget/), and [ImageMagick](https://imagemagick.org/).

BindSympli preprocessor code is written in Python, but it uses the external script written in JavaScript. This script is provided in BindSympli package:

```bash
$ pip install foliantcontrib.bindsympli
```

## Config

To enable the preprocessor, add `bindsympli` to `preprocessors` section in the project config:

```yaml
preprocessors:
    - bindsympli
```

The preprocessor has a number of options with the following default values:

```yaml
preprocessors:
    - bindsympli:
        get_sympli_img_urls_path: get_sympli_img_urls.js
        wget_path: wget
        convert_path: convert
        cache_dir: !path .bindsymplicache
        sympli_login: ''
        sympli_password: ''
        image_width: 800
        max_attempts: 5
```

`get_sympli_img_urls_path`
:   Path to the script `get_sympli_img_urls.js` or alternative command that launches it (e.g. `node some_another_script.js`). By default, it is assumed that you have this command and all other commands in `PATH`.

`wget_path`
:   Path to `wget` binary.

`convert_path`
:   Path to `convert` binary, a part of ImageMagick.

`cache_dir`
:   Directory to store downloaded and resized images.

`sympli_login`
:   Your username in Sympli account.

`sympli_password`
:   Your password in Sympli account.

`image_width`
:   Width of resulting images in pixels (original images are too large).

`max_attempts`
:   Maximum number of attempts to run the script `get_sympli_img_urls.js` on fails.

## Usage

To insert a design layout image from Sympli into your documentation, use `<<sympli>...</sympli>` tags in Markdown source:

```markdown
Here’s an image from Sympli:

<<sympli caption="An optional caption" url="https://app.sympli.io/app#!/designs/0123456789abcdef01234567/specs/assets"></sympli>
```

You have to specify the URL of Sympli design layout page in `url` attribute.

BindSympli preprocessor will replace such blocks with local image references.
