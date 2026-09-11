"""Build a Linux Lambda zip locally without connecting to AWS."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    output=args.output.resolve()
    if not (root/'dist/index.html').is_file():
        raise SystemExit('Run pnpm build before packaging.')
    if output.exists():
        raise SystemExit('Choose a new output path to preserve existing build artifacts.')
    output.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='kind-lambda-',dir=output.parent))
    # uv evaluates dependency markers for Linux even when the build host is Windows.
    subprocess.run([sys.executable,'-m','uv','pip','install','--quiet','--python-platform','x86_64-manylinux2014',
        '--python-version','3.12','--only-binary',':all:',
        '--target',str(stage),'-r',str(root/'infra/requirements-lambda-lock.txt')],check=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(stage.rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts:
                archive.write(file,file.relative_to(stage).as_posix())
        for directory in ('server','dist'):
            for file in sorted((root/directory).rglob('*')):
                if file.is_file() and '__pycache__' not in file.parts and not file.name.startswith('test_'):
                    archive.write(file,file.relative_to(root).as_posix())
    with zipfile.ZipFile(output) as archive:
        size=sum(info.file_size for info in archive.infolist())
        if size >= 250*1024*1024:
            raise SystemExit('Package exceeds the Lambda uncompressed size limit.')
        required={'server/lambda_entry.py','server/cloud_store.py','server/auth.py','dist/index.html','mangum/__init__.py','strands/__init__.py'}
        if not required.issubset(set(archive.namelist())):
            raise SystemExit('Package is missing a required runtime file.')
    manifest={'file':output.name,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'compressed_bytes':output.stat().st_size,'uncompressed_bytes':size,
        'runtime':'python3.12','architecture':'x86_64','platform':'manylinux2014_x86_64',
        'verification':'Package contents checked locally; Lambda execution still requires a cloud smoke test.'}
    output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    main()
