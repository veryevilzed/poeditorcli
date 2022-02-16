#!/usr/bin/env python

import os, logging, click, sys
try:
    from upload import POEditorUpload
    from update import POEditorUpdate
    from release import POEditorRelease
except:
    from .upload import POEditorUpload
    from .update import POEditorUpdate
    from .release import POEditorRelease
    
FORMAT = '%(asctime)-7s [%(name)-6s] [%(levelname)-5s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt="%H:%M:%S")

log = logging.getLogger("main")

log.debug("POEditorCli")


@click.group()
def cli():
    pass

@cli.command()
@click.option('--translation', default="base.yaml", help='Base translation Name')
@click.option('--api_token', default=None, envvar="POEDITOR_API_TOKEN", help='POEditor api-token')
@click.option('--project_id', default=None, help='POEditor Project ID')
@click.option('--language', default='ru', help='Language')
@click.option('--collect_path', default=None, help='Path to collect parts')
@click.option('--cleanup', default=False, is_flag=True, help='Force delete unused terms')
def upload(translation, api_token, project_id, language, collect_path, cleanup):
    if api_token is None:
        api_token = os.environ.get('POEDITOR_API_TOKEN')
    POEditorUpload(translation, api_token, project_id, language, collect_path, cleanup)


@cli.command()
@click.option('--translation', default="base.yaml", help='Base translation Name')
@click.option('--api_token', default=None, envvar="POEDITOR_API_TOKEN", help='POEditor api-token')
@click.option('--project_id', default=None, help='POEditor Project ID')
@click.option('--language', default=None, help='Language. if not set, load all languages. Need %s in translation name')
@click.option('--except_language', default=None, help='Except language for `load all language`')
def update(translation, api_token, project_id, language, except_language):
    if language is None:
        if "%s" not in translation:
            log.error("Need %s for language code")
            sys.exit(9)

        POEditorUpdate.getLanguageList(translation, api_token, project_id, except_language)
    else:
        POEditorUpdate(translation, api_token, project_id, language)


@cli.command()
@click.option('--api_token', default=None, envvar="POEDITOR_API_TOKEN", help='POEditor api-token')
@click.option('--project_id', default=None, help='POEditor Project ID')
@click.option('--languages', default=None, help='Languages configuration: en,ru;es,en;...')
@click.option('--upload_url', default=None, help='Upload URL')
@click.option('--upload_token', default=None, help='Upload token')
@click.option('--upload_version', default=0, help='Upload version')
def release(api_token, project_id, languages, upload_url, upload_token, upload_version):
    if upload_url is None or upload_token is None:
        log.error("Upload URL and Token must be set")
        sys.exit(9)

    if languages is None:
        log.error("Languages configuration must be set")
        sys.exit(9)

    if 'http' not in upload_url:
        upload_url = 'http://%s/update/language' % upload_url

    languages = [x.split("-") for x in languages.split(",")]

    try:
        languages_used = Set()
    except:
        languages_used = set()
    log.info("Languages configuration will be:")
    for lang in languages:
        log.info("\t%s", " <= ".join(lang))
        languages_used.update(lang)

    log.info("Total used languages: %s", ", ".join(languages_used))

    POEditorRelease(api_token, project_id, languages, languages_used, upload_url, upload_token, int(upload_version))

@cli.command()
def version():
    print("Version: 0.10")

if __name__ == '__main__':
    cli()
