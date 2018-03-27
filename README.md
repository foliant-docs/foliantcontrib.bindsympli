# BindSympli

BindSympli is a tool to download design layout images from [Sympli](https://sympli.io/) CDN using certain [Sympli](https://sympli.io/) account, to resize these images, and to bind them with the documentation project.

## Installation

Before using BindSympli, you need to install [Node.js](https://nodejs.org/en/), [Puppeteer](https://github.com/GoogleChrome/puppeteer), [wget](https://www.gnu.org/software/wget/), and [ImageMagick](https://imagemagick.org/).

BindSympli preprocessor code is written in Python, but it uses external scripts written in JavaScript and Perl. These scripts are provided in BindSympli package:

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
        get_sympli_design_urls_path: get_sympli_design_urls.pl
        get_sympli_img_urls_path: get_sympli_img_urls.js
        bind_sympli_imgs_path: bind_sympli_imgs.pl
        wget_path: wget
        convert_path: convert
        cache_dir: !path bindsymplicache
        sympli_login: ''
        sympli_password: ''
        image_width: 800
```

`get_sympli_design_urls_path`
:   Path to the script `get_sympli_design_urls.pl` or alternative command that launches it (e.g. `perl /home/my_username/some_script.pl`). By default, it is assumed that you have this command and all other commands in `PATH`.

`get_sympli_img_urls_path`
:   Path to the script `get_sympli_img_urls.js` or alternative command that launches it (e.g. `node some_another_script.js`).

`bind_sympli_imgs_path`
:   Path to the script `bind_sympli_imgs.pl` or alternative command that launches it (e.g. `/usr/bin/perl /path/to/one_more_script.pl`).

`wget_path`
:   Path to `wget` binary.

`convert_path`
:   Path to `convert` binary, a part of [ImageMagick](https://imagemagick.org/).

`cache_dir`
:   Directory to store downloaded and resized images.

`sympli_login`
:   Your username in [Sympli](https://sympli.io/) account.

`sympli_password`
:   Your password in [Sympli](https://sympli.io/) account.

`image_width`
:   Width of resulting images in pixels (original images are too large).
