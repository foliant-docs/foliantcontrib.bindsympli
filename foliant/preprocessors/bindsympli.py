'''
Preprocessor for Foliant documentation authoring tool.
Downloads design layout images from Sympli CDN
using certain Sympli account, resizes these images
and binds them with the documentation project.

Uses Node.js, headless Chrome, Puppeteer, wget, and external
scripts written in Perl and JavaScript. These scripts,
as specified in the installator, must be located in
``/usr/local/bin`` directory, must be added to ``PATH``,
and must be executable. These conditions may be overridden
in the config.
'''

from pathlib import Path
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'get_sympli_design_urls_path': 'get_sympli_design_urls.pl',
        'get_sympli_img_urls_path': 'get_sympli_img_urls.js',
        'bind_sympli_imgs_path': 'bind_sympli_imgs.pl',
        'wget_path': 'wget',
        'convert_path': 'convert',
        'cache_dir': Path('.bindsymplicache'),
        'sympli_login': '',
        'sympli_password': '',
        'image_width': 800,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply(self):
        self.options["cache_dir"].mkdir(parents=True, exist_ok=True)

        try:
            command = f'{self.options["get_sympli_design_urls_path"]} ' \
                      f'{self.working_dir.absolute().as_posix()} ' \
                      f'{self.options["cache_dir"].absolute().as_posix()} '
            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

        except CalledProcessError as exception:
            raise RuntimeError(f'Failed: {exception.output.decode()}')

        try:
            command = f'{self.options["get_sympli_img_urls_path"]} ' \
                      f'{self.options["cache_dir"].absolute().as_posix()} ' \
                      f'{self.options["sympli_login"]} ' \
                      f'{self.options["sympli_password"]}'
            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

        except CalledProcessError as exception:
            raise RuntimeError(f'Failed: {exception.output.decode()}')

        try:
            command = f'{self.options["bind_sympli_imgs_path"]} ' \
                      f'{self.working_dir.absolute().as_posix()} ' \
                      f'{self.options["cache_dir"].absolute().as_posix()} ' \
                      f'{self.options["image_width"]} ' \
                      f'"{self.options["wget_path"]}" ' \
                      f'"{self.options["convert_path"]}"'
            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

        except CalledProcessError as exception:
            raise RuntimeError(f'Failed: {exception.output.decode()}')
