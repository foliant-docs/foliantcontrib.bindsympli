'''
Preprocessor for Foliant documentation authoring tool.
Downloads design layout images from Sympli CDN
using certain Sympli account, resizes these images
and binds them with the documentation project.

Uses Node.js, headless Chrome, Puppeteer, wget, and external
script written in JavaScript. This script, as specified
in the installator, must be located in ``/usr/local/bin``
directory, must be added to ``PATH``, and must be executable.
These conditions may be overridden in the config.
'''

import re
from pathlib import Path
from hashlib import md5
from subprocess import run, PIPE, STDOUT, CalledProcessError
from typing import Dict
OptionValue = int or float or bool or str

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'get_sympli_img_urls_path': 'get_sympli_img_urls.js',
        'wget_path': 'wget',
        'convert_path': 'convert',
        'cache_dir': Path('.bindsymplicache'),
        'sympli_login': '',
        'sympli_password': '',
        'image_width': 800,
    }

    tags = 'sympli',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cache_dir_path = self.project_path / self.options['cache_dir']
        self._design_urls_file_path = self._cache_dir_path / 'design_urls.txt'
        self._img_urls_file_path = self._cache_dir_path / 'img_urls.txt'

        self._img_urls = {}

    def _get_img_hash(self, img_url: str, resized: bool) -> str:
        img_hash = md5(f'{img_url}'.encode())

        if resized:
            img_hash.update(f'{self.options["image_width"]}'.encode())

        return f'{img_hash.hexdigest()}'

    def _process_sympli(self, options: Dict[str, OptionValue]) -> str:
        resized_img_path = self._cache_dir_path / f'resized_{self._get_img_hash(self._img_urls[options.get("url", "")], True)}.png'
        resized_img_ref = f'![{options.get("caption", "")}]({resized_img_path.absolute().as_posix()})'
        return resized_img_ref

    def process_sympli(self, markdown_content: str) -> str:
        def _sub(design_definition) -> str:
            return self._process_sympli(self.get_options(design_definition.group('options')))

        return self.pattern.sub(_sub, markdown_content)

    def apply(self):
        design_urls = []

        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                markdown_content = markdown_file.read()

            design_definitions = re.finditer(self.pattern, markdown_content)

            for design_definition in design_definitions:
                design_url = self.get_options(design_definition.group('options')).get('url', '')

                if design_url not in design_urls:
                    design_urls.append(design_url)

        if design_urls:
            self._cache_dir_path.mkdir(parents=True, exist_ok=True)

            if self._design_urls_file_path.exists():
                self._design_urls_file_path.unlink()

            with open(self._design_urls_file_path, 'w', encoding='utf8') as design_urls_file:
                design_urls_file.write("\n".join(design_urls) + "\n")

            try:
                command = f'{self.options["get_sympli_img_urls_path"]} ' \
                          f'{self._cache_dir_path.absolute().as_posix()} ' \
                          f'{self.options["sympli_login"]} ' \
                          f'{self.options["sympli_password"]}'
                run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

            except CalledProcessError as exception:
                raise RuntimeError(f'Failed: {exception.output.decode()}')

            with open(self._img_urls_file_path, encoding='utf8') as img_urls_file:
                for line in img_urls_file:
                    (design_url, img_url) = line.split()

                    self._img_urls[design_url] = img_url

                    original_img_path = self._cache_dir_path / f'original_{self._get_img_hash(img_url, False)}.png'

                    if not original_img_path.exists():
                        try:
                            command = f'{self.options["wget_path"]} ' \
                                      f'-O {original_img_path.absolute().as_posix()} ' \
                                      f'{img_url}'
                            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                        except CalledProcessError as exception:
                            raise RuntimeError(f'Failed: {exception.output.decode()}')

                    resized_img_path = self._cache_dir_path / f'resized_{self._get_img_hash(img_url, True)}.png'

                    if not resized_img_path.exists():
                        try:
                            command = f'{self.options["convert_path"]} ' \
                                      f'{original_img_path.absolute().as_posix()} ' \
                                      f'-resize {self.options["image_width"]} ' \
                                      f'{resized_img_path.absolute().as_posix()}'
                            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                        except CalledProcessError as exception:
                            raise RuntimeError(f'Failed: {exception.output.decode()}')

            for markdown_file_path in self.working_dir.rglob('*.md'):
                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    markdown_content = markdown_file.read()

                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    markdown_file.write(self.process_sympli(markdown_content))
