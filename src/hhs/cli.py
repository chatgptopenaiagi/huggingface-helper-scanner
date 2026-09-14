"""JSON CLI; explicit output writes, no package installation needed."""
import argparse
import json
from pathlib import Path
import sys

from .hf.client import Client, Limits, Response
from .hf.inspector import inspect_repository


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'HHS: invalid CLI arguments; use --help.\n')


def main(argv=None):
    parser=SafeParser(prog='hhs')
    commands=parser.add_subparsers(dest='command',required=True)
    inspect=commands.add_parser('inspect-hf',help='Observe bounded public model repository metadata only')
    inspect.add_argument('url')
    inspect.add_argument('--revision')
    inspect.add_argument('--output',type=Path)
    inspect.add_argument('--offline-fixture',type=Path,help='Synthetic model-info JSON; never contacts the network')
    inspect.add_argument('--max-files',type=int,default=1000)
    inspect.add_argument('--timeout',type=float,default=10.0)
    args=parser.parse_args(argv)
    try:
        limits=Limits(timeout=args.timeout,max_files=args.max_files)
        client=Client(limits)
        if args.offline_fixture:
            with args.offline_fixture.open('rb') as handle:
                body=handle.read(limits.max_response_bytes+1)
            client=Client(limits,transport=lambda target,limits:Response(200,{},body),mode='offline_fixture')
        result=inspect_repository(args.url,args.revision,client)
        output=json.dumps(result,indent=2,ensure_ascii=True,allow_nan=False)+'\n'
        if args.output:
            # Exclusive create avoids accidentally replacing source, fixtures or prior reports.
            with args.output.open('x',encoding='utf-8') as handle: handle.write(output)
        else: sys.stdout.write(output)
        return 0 if result['status']=='OK' else 2
    except (OSError,ValueError):
        sys.stderr.write('HHS: invalid limits or local fixture/output operation failed; details omitted.\n')
        return 2
