#!/usr/bin/env python

import os, logging, click, sys
from upload import POEditorUpload
from update import POEditorUpdate

FORMAT = '%(asctime)-7s [%(name)-6s] [%(levelname)-5s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt="%H:%M:%S")

log = logging.getLogger("main")

log.debug("POEditorCli")


@click.group()
def cli():
    pass

@cli.command()
@click.option('--translation', default="base.yaml", help='Base translation Name')
@click.option('--api_token', default=None, help='POEditor api-token')
@click.option('--project_id', default=None, help='POEditor Project ID')
@click.option('--language', default='ru', help='Language')
@click.option('--collect_path', default=None, help='Path to collect parts')
@click.option('-f', '--force_delete', default=False, is_flag=True, help='Force delete unused terms')
def upload(translation, api_token, project_id, language, collect_path, force_delete):
    if api_token is None:
        api_token = os.environ.get('POEDITOR_API_TOKEN')
    POEditorUpload(translation, api_token, project_id, language, collect_path, force_delete)


@cli.command()
@click.option('--translation', default="base.yaml", help='Base translation Name')
@click.option('--api_token', default="lima-assets", help='POEditor api-token')
@click.option('--project_id', default=None, help='POEditor Project ID')
@click.option('--language', default=None, help='Language. if not set, load all languages. Need %s in translation name')
@click.option('--except_language', default=None, help='Except language for `load all language`')
def update(translation, api_token, project_id, language, except_language):
    if api_token is None:
        api_token = os.environ.get('POEDITOR_API_TOKEN')
    if language is None:
        if "%s" not in translation:
            log.error("Need %s for language code")
            sys.exit(9)

        POEditorUpdate.getLanguageList(translation, api_token, project_id, except_language)
    else:
        POEditorUpdate(translation, api_token, project_id, language)


if __name__ == '__main__':
    cli()
