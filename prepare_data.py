from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from zipfile import ZipFile


def main():
    root = Path(__file__).resolve().parent
    relative_path = 'model/data/debase_db.sqllite3'
    target = root / relative_path
    if target.is_file():
        print(f'Base déjà présente : {relative_path}')
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(root / 'site-amelie.zip') as archive:
        with TemporaryDirectory(dir=target.parent) as directory:
            temporary_file = Path(directory) / target.name
            with archive.open(f'SAE 1.01/{relative_path}') as source, temporary_file.open('wb') as output:
                copyfileobj(source, output)
            temporary_file.replace(target)

    print(f'Base disponible : {relative_path}')


if __name__ == '__main__':
    main()
