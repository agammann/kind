"""Verify the approved hosted sample workflow without printing access credentials."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import httpx


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True)
    parser.add_argument('--access-file',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--allow-live',action='store_true',required=True)
    args=parser.parse_args()
    code=json.loads(args.access_file.read_text())['access_code']
    evidence={'url':args.url,'checked_at':datetime.now(timezone.utc).isoformat(),'checks':[]}
    def passed(name):
        evidence['checks'].append(name)
        print(name,flush=True)
    def request(client,method,path,**kwargs):
        time.sleep(0.5)
        for attempt in range(5):
            response=client.request(method,path,**kwargs)
            # Retry only API Gateway throttles, not an application admission limit.
            if response.status_code!=429 or 'detail' in response.text or attempt==4:
                return response
            time.sleep(2)
    def data(response,expected=200):
        assert response.status_code==expected, f'Unexpected HTTP status {response.status_code}, expected {expected}'
        return response.json()
    with httpx.Client(base_url=args.url,timeout=40) as owner,httpx.Client(base_url=args.url,timeout=40) as volunteer:
        health=data(request(owner,'GET','/api/health'))
        assert health['bedrock_configured']
        passed('Hosted API reports live model configuration')
        assert request(volunteer,'GET','/api/workspace').status_code==401
        assert request(volunteer,'POST','/api/session',json={}).status_code==401
        assert request(volunteer,'POST','/api/session',json={'access_code':'incorrect-verification-code'}).status_code==401
        passed('Anonymous workspace access and incorrect coordinator login are rejected')
        login=request(owner,'POST','/api/session',json={'access_code':code})
        data(login)
        assert 'Secure' in login.headers.get('set-cookie','') and 'HttpOnly' in login.headers.get('set-cookie','')
        passed('Coordinator login issues a secure HTTPOnly cookie')
        assert request(owner,'POST','/api/scan',headers={'Origin':'https://untrusted.example'},json={}).status_code==403
        passed('Cross origin mutation is rejected')
        before=data(request(owner,'GET','/api/workspace'))
        assert before['hosted'] and before['sample_data']
        shift=next(s for s in before['shifts'] if s['id']=='s1')
        assert len(shift['assigned'])<shift['required'],'Verification requires the initial open sample shift'
        job=data(request(owner,'POST','/api/shifts/s1/prepare',json={'mode':'bedrock'}),202)
        passed('Live AI request is admitted as an asynchronous job')
        for _ in range(150):
            time.sleep(2)
            status=data(request(owner,'GET','/api/jobs/'+job['job_id']))
            if status['status'] in ('complete','failed'):
                break
        assert status['status']=='complete','Live preparation did not complete; inspect the private worker diagnostics'
        result=status['result']
        invitation=result['invitation']
        assert invitation['source']=='bedrock' and invitation['status']=='draft' and 'token' not in invitation
        evidence['agent_tools']=[entry['tool'] for entry in result['trace']]
        assert {'get_shift_context','check_eligibility','prepare_invitation'} <= set(evidence['agent_tools'])
        after_draft=data(request(owner,'GET','/api/workspace'))
        assert next(s for s in after_draft['shifts'] if s['id']=='s1')['assigned']==shift['assigned']
        passed('Real Strands tool loop saves an unapproved draft without changing the roster')
        assert request(volunteer,'POST',f"/api/invitations/{invitation['id']}/approve",json={'message':invitation['message']}).status_code==401
        approved=data(request(owner,'POST',f"/api/invitations/{invitation['id']}/approve",json={'message':invitation['message']}))
        public=data(request(volunteer,'GET','/api/volunteer/'+approved['token']))
        assert 'volunteers' not in public and 'assigned' not in public['shift']
        passed('Only coordinator approval activates the scoped volunteer response page')
        accepted=data(request(volunteer,'POST','/api/volunteer/'+approved['token']+'/respond',json={'decision':'accepted'}))
        assert accepted['status']=='accepted'
        repeated=data(request(volunteer,'POST','/api/volunteer/'+approved['token']+'/respond',json={'decision':'accepted'}))
        assert repeated['status']=='accepted'
        roster=data(request(owner,'GET','/api/workspace'))
        covered=next(s for s in roster['shifts'] if s['id']=='s1')
        assert len(covered['assigned'])==covered['required'] and invitation['volunteer_id'] in covered['assigned']
        passed('Acceptance fills the shift and repeated acceptance does not overfill it')
        data(request(owner,'POST','/api/logout',json={}))
        assert request(owner,'GET','/api/workspace').status_code==401
        data(request(owner,'POST','/api/session',json={'access_code':code}))
        saved=data(request(owner,'GET','/api/workspace'))
        assert next(s for s in saved['shifts'] if s['id']=='s1')['assigned']==covered['assigned']
        passed('Roster remains saved after sign out and a new coordinator session')
    evidence['status']='passed'
    evidence['scope']='One live Bedrock sample preparation, explicit approval and volunteer acceptance through the public HTTPS API. No external messages or real people.'
    args.report.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
