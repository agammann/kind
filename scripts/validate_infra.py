"""Run local schema and selected Guard checks; write a portable evidence report."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone


def decode_guard(text):
    records=[]
    decoder=json.JSONDecoder()
    while text.strip():
        record,end=decoder.raw_decode(text.lstrip())
        records.append(record)
        text=text.lstrip()[end:]
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lint',required=True)
    parser.add_argument('--guard',required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    templates=['infra/artifacts.json','infra/template.json']
    lint=subprocess.run([args.lint,'--regions','us-west-2','--template',*templates,'--format','json'],cwd=root,text=True,capture_output=True)
    guard=subprocess.run([args.guard,'validate','--rules','infra/guard','--data',templates[0],'--data',templates[1],
        '--output-format','json','--show-summary','none'],cwd=root,text=True,capture_output=True)
    lint_results=json.loads(lint.stdout or '[]')
    records=decode_guard(guard.stdout)
    guard_results=[{'template':Path(r['name'].replace('\\','/')).name,'status':r['status'],
        'passed':r.get('compliant',[]),'skipped':r.get('not_applicable',[]),'failed':r.get('not_compliant',[])} for r in records]
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'region':'us-west-2',
        'versions':{'cfn_lint':subprocess.check_output([args.lint,'--version'],text=True).strip(),
            'cfn_guard':subprocess.check_output([args.guard,'--version'],text=True).strip()},
        'templates':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in templates},
        'schema_exit_code':lint.returncode,'schema_findings':lint_results,
        'guard_exit_code':guard.returncode,'guard_checks':guard_results,
        'tool_errors':[x for x in [lint.stderr.strip(),guard.stderr.strip()] if x],
        'scope':'Local template validation only. Cloud account checks and change set validation are still required.'}
    destination=root/'docs/infra-validation.json'
    destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'schema_exit_code':lint.returncode,'schema_findings':lint_results,'guard_exit_code':guard.returncode,
        'guard_passes':sum(len(r['passed']) for r in guard_results),'guard_skips':sum(len(r['skipped']) for r in guard_results),
        'guard_failures':[r for r in guard_results if r['failed']], 'errors':report['tool_errors']},indent=2))
    if lint.returncode or guard.returncode:
        raise SystemExit(1)


if __name__=='__main__':
    main()
