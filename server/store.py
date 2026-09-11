"""SQLite-backed, transactional workflow. Model output never authorizes side effects."""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path


class WorkflowError(Exception):
    def __init__(self, message: str, status: int = 409):
        self.message, self.status = message, status


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat()


def parse(value: str) -> datetime:
    return datetime.fromisoformat(value)


def event(state, title, detail, shift_id=None):
    state['activity'].insert(0, {'id': secrets.token_hex(8), 'title': title,
        'detail': detail, 'shift_id': shift_id, 'at': iso(utcnow())})
    state['activity'] = state['activity'][:200]


def seed_state():
    now = utcnow()
    # Start on the next Saturday, with explicit UTC timestamps and displayed timezone.
    day = (now + timedelta(days=(5 - now.weekday()) % 7 or 7)).replace(hour=16, minute=0, second=0, microsecond=0)
    shifts = [
        {'id':'s1','title':'Saturday food distribution','start':iso(day),'end':iso(day+timedelta(hours=3)), 'location':'Riverbend Community Pantry','required':2,'qualification':'Food handling','assigned':['v3']},
        {'id':'s2','title':'Pantry preparation','start':iso(day+timedelta(days=1)),'end':iso(day+timedelta(days=1,hours=2)), 'location':'Riverbend Community Pantry','required':1,'qualification':'Food handling','assigned':[]},
        {'id':'s3','title':'Community deliveries','start':iso(day+timedelta(days=2)),'end':iso(day+timedelta(days=2,hours=3)), 'location':'Riverbend loading dock','required':1,'qualification':'Driver','assigned':['v2']},
    ]
    names = [('v1','Maya Chen',['Food handling'],True,0),('v2','Jordan Ellis',['Driver','Food handling'],True,2),
             ('v3','Aisha Patel',['Food handling'],True,1),('v4','Leo Rivera',['Driver'],True,0),
             ('v5','Sam Brooks',['Food handling'],True,3),('v6','Nina Park',['Food handling'],False,0)]
    volunteers = [{'id':vid,'name':name,'qualifications':quals,'opted_in':opted,
                   'recent_contacts':contacts,'contact_counted_at':iso(now),
                   'availability':[{'start':iso(day-timedelta(days=1)), 'end':iso(day+timedelta(days=10))}]} for vid,name,quals,opted,contacts in names]
    state = {'organization':'Riverbend Food Bank','sample_data':True,'timezone':'America/Los_Angeles',
             'shifts':shifts,'volunteers':volunteers,'invitations':[],'activity':[],'scanned_gaps':[], 'agent_runs':[]}
    event(state,'Sample workspace ready','Fictional volunteers and shifts. No external messages are sent.')
    return state


class Store:
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv('KIND_DB_PATH', 'data/kind.sqlite3')
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS workspace (id INTEGER PRIMARY KEY CHECK(id=1), document TEXT NOT NULL)')
            conn.execute('INSERT OR IGNORE INTO workspace VALUES (1, ?)', (json.dumps(seed_state()),))

    def connect(self):
        conn = sqlite3.connect(self.path, timeout=15)
        conn.execute('PRAGMA journal_mode=WAL')
        return conn

    @contextmanager
    def transaction(self):
        with self.connect() as conn:
            conn.execute('BEGIN IMMEDIATE')
            state = json.loads(conn.execute('SELECT document FROM workspace WHERE id=1').fetchone()[0])
            yield state
            conn.execute('UPDATE workspace SET document=? WHERE id=1', (json.dumps(state),))

    def read(self):
        with self.connect() as conn:
            return json.loads(conn.execute('SELECT document FROM workspace WHERE id=1').fetchone()[0])

    @staticmethod
    def find(state, collection, item_id):
        item = next((x for x in state[collection] if x['id']==item_id),None)
        if item is None:
            raise WorkflowError('This record was not found.',404)
        return item

    @staticmethod
    def reasons(state, shift, volunteer):
        reasons = []
        if parse(shift['start']) <= utcnow(): reasons.append('The shift has already started')
        if not volunteer['opted_in']: reasons.append('Not accepting invitations')
        if shift['qualification'] not in volunteer['qualifications']: reasons.append('Required qualification is missing')
        if not any(parse(a['start'])<=parse(shift['start']) and parse(a['end'])>=parse(shift['end']) for a in volunteer['availability']):
            reasons.append('Not available for the entire shift')
        if volunteer['id'] in shift['assigned']: reasons.append('Already assigned to this shift')
        for other in state['shifts']:
            if other['id']!=shift['id'] and volunteer['id'] in other['assigned'] and parse(other['start'])<parse(shift['end']) and parse(other['end'])>parse(shift['start']):
                reasons.append('Has an overlapping commitment')
        return reasons

    @staticmethod
    def contacts(state, volunteer):
        cutoff=utcnow()-timedelta(days=7)
        baseline=volunteer['recent_contacts'] if parse(volunteer['contact_counted_at'])>=cutoff else 0
        return baseline+sum(1 for i in state['invitations'] if i['volunteer_id']==volunteer['id'] and i.get('approved_at') and parse(i['approved_at'])>=cutoff)

    def candidates(self, shift_id):
        state=self.read()
        shift=self.find(state,'shifts',shift_id)
        eligible,excluded=[],[]
        for volunteer in state['volunteers']:
            reasons=self.reasons(state,shift,volunteer)
            contacts=self.contacts(state,volunteer)
            if contacts>=3: reasons.append('Weekly invitation limit reached')
            if any(i['shift_id']==shift_id and i['volunteer_id']==volunteer['id'] and i['status'] in ('draft','pending','declined','accepted') for i in state['invitations']):
                reasons.append('Already invited for this shift')
            record={'id':volunteer['id'],'name':volunteer['name'],'contacts':contacts,'reasons':reasons,
                    'qualifications':volunteer['qualifications']}
            if reasons: excluded.append(record)
            else: eligible.append(record)
        eligible.sort(key=lambda v:(v['contacts'],v['name']))
        return {'eligible':eligible,'excluded':excluded,'shift':shift}

    def draft(self, shift_id, volunteer_id, message, source='rules'):
        if not message.strip() or len(message)>2000: raise WorkflowError('Invitation must contain 1–2,000 characters.',422)
        with self.transaction() as state:
            shift=self.find(state,'shifts',shift_id)
            volunteer=self.find(state,'volunteers',volunteer_id)
            if len(shift['assigned'])>=shift['required']: raise WorkflowError('This shift is already covered.')
            reasons=self.reasons(state,shift,volunteer)
            if self.contacts(state,volunteer)>=3: reasons.append('Weekly invitation limit reached')
            if reasons: raise WorkflowError('; '.join(reasons))
            existing=next((i for i in state['invitations'] if i['shift_id']==shift_id and i['volunteer_id']==volunteer_id and i['status'] in ('draft','pending','declined','accepted')),None)
            if existing: raise WorkflowError('This volunteer has already been invited for this shift.')
            invitation={'id':secrets.token_hex(12),'shift_id':shift_id,'volunteer_id':volunteer_id,
                        'message':message.strip(),'status':'draft','created_at':iso(utcnow()),'source':source}
            state['invitations'].append(invitation)
            event(state,'Invitation prepared',f"Draft for {volunteer['name']}; waiting for your approval.",shift_id)
            return invitation

    def approve(self, invitation_id, message):
        if not message.strip() or len(message)>2000: raise WorkflowError('Invitation must contain 1–2,000 characters.',422)
        with self.transaction() as state:
            invitation=self.find(state,'invitations',invitation_id)
            if invitation['status']=='pending': return invitation
            if invitation['status']!='draft': raise WorkflowError('Only a draft invitation can be approved.')
            shift=self.find(state,'shifts',invitation['shift_id'])
            volunteer=self.find(state,'volunteers',invitation['volunteer_id'])
            if len(shift['assigned'])>=shift['required']: raise WorkflowError('This shift is already covered.')
            reasons=self.reasons(state,shift,volunteer)
            if self.contacts(state,volunteer)>=3: reasons.append('Weekly invitation limit reached')
            if reasons: raise WorkflowError('; '.join(reasons))
            invitation.update(status='pending',message=message.strip(),token=secrets.token_urlsafe(32),approved_at=iso(utcnow()),expires_at=shift['start'])
            event(state,'Invitation approved',f"A response link is ready for {volunteer['name']}. No email or text was sent.",shift['id'])
            return invitation

    def cancel_invitation(self, invitation_id):
        with self.transaction() as state:
            invitation=self.find(state,'invitations',invitation_id)
            if invitation['status'] not in ('draft','pending'): raise WorkflowError('This invitation is already closed.')
            invitation['status']='cancelled'
            event(state,'Invitation cancelled','The invitation can no longer be accepted.',invitation['shift_id'])

    def invitation_by_token(self, state, token):
        invitation=next((i for i in state['invitations'] if i.get('token') and secrets.compare_digest(i['token'],token)),None)
        if invitation is None: raise WorkflowError('This invitation link was not found.',404)
        return invitation

    def public_invitation(self, token):
        state=self.read()
        invitation=self.invitation_by_token(state,token)
        shift=self.find(state,'shifts',invitation['shift_id'])
        volunteer=self.find(state,'volunteers',invitation['volunteer_id'])
        status=invitation['status']
        if status=='pending' and parse(invitation['expires_at'])<=utcnow(): status='expired'
        return {'organization':state['organization'],'sample_data':True,'name':volunteer['name'],
                'message':invitation['message'],'status':status,'shift':{k:shift[k] for k in ('title','start','end','location','qualification')},'timezone':state['timezone']}

    def respond(self, token, decision):
        if decision not in ('accepted','declined'): raise WorkflowError('Choose accept or decline.',422)
        with self.transaction() as state:
            invitation=self.invitation_by_token(state,token)
            if invitation['status']==decision: return {'status':decision}
            if invitation['status']!='pending': raise WorkflowError('This invitation is already closed.')
            if parse(invitation['expires_at'])<=utcnow(): raise WorkflowError('This invitation has expired.')
            shift=self.find(state,'shifts',invitation['shift_id'])
            volunteer=self.find(state,'volunteers',invitation['volunteer_id'])
            if decision=='accepted':
                if len(shift['assigned'])>=shift['required']: raise WorkflowError('This shift has already been filled. Thank you for offering to help.')
                reasons=self.reasons(state,shift,volunteer)
                if reasons: raise WorkflowError('Availability or eligibility changed. Please contact the coordinator.')
                shift['assigned'].append(volunteer['id'])
                if len(shift['assigned'])>=shift['required']:
                    for other in state['invitations']:
                        if other['id']!=invitation['id'] and other['shift_id']==shift['id'] and other['status'] in ('pending','draft'):
                            other['status']='filled'
            invitation.update(status=decision,responded_at=iso(utcnow()))
            event(state,'Shift covered' if decision=='accepted' and len(shift['assigned'])>=shift['required'] else 'Volunteer '+decision,
                  f"{volunteer['name']} {'joined' if decision=='accepted' else 'declined'} {shift['title']}.",shift['id'])
            return {'status':decision}

    def cancel_assignment(self, shift_id, volunteer_id):
        with self.transaction() as state:
            shift=self.find(state,'shifts',shift_id)
            volunteer=self.find(state,'volunteers',volunteer_id)
            if volunteer_id not in shift['assigned']: raise WorkflowError('This volunteer is not assigned.')
            shift['assigned'].remove(volunteer_id)
            for invitation in state['invitations']:
                if invitation['shift_id']==shift_id and invitation['volunteer_id']==volunteer_id and invitation['status']=='accepted': invitation['status']='cancelled'
            # Do not automatically re-invite a volunteer who just cancelled.
            state['invitations'].append({'id':secrets.token_hex(12),'shift_id':shift_id,'volunteer_id':volunteer_id,'status':'declined','source':'cancellation','message':'Assignment cancelled by coordinator','created_at':iso(utcnow())})
            event(state,'Volunteer cancellation',f"{volunteer['name']} was removed from {shift['title']}.",shift_id)
            if shift_id in state['scanned_gaps']: state['scanned_gaps'].remove(shift_id)

    def scan(self):
        with self.transaction() as state:
            count=0
            for shift in state['shifts']:
                for invitation in state['invitations']:
                    if invitation['shift_id']==shift['id'] and invitation['status'] in ('draft','pending') and parse(shift['start'])<=utcnow(): invitation['status']='expired'
                if len(shift['assigned'])<shift['required'] and parse(shift['start'])>utcnow():
                    count+=1
                    if shift['id'] not in state['scanned_gaps']:
                        event(state,'Coverage gap detected',f"{shift['title']} needs {shift['required']-len(shift['assigned'])} more volunteer(s).",shift['id'])
                        state['scanned_gaps'].append(shift['id'])
            return {'open_shifts':count}

    def save_run(self, shift_id, source, trace, result):
        with self.transaction() as state:
            state['agent_runs'].insert(0,{'id':secrets.token_hex(8),'at':iso(utcnow()),'shift_id':shift_id,'source':source,'trace':trace,'result':result})
            state['agent_runs']=state['agent_runs'][:30]

