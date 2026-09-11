import {useEffect,useState} from 'react';
import {CheckCircle2,HeartHandshake,ArrowLeft} from 'lucide-react';
import {api} from './api';
import {ShiftDetails,ShiftTime,Status} from './components';
import type {PublicInvitation} from './types';

export default function VolunteerPage({token}:{token:string}){
 const [invitation,setInvitation]=useState<PublicInvitation|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 useEffect(()=>{api<PublicInvitation>('/volunteer/'+encodeURIComponent(token)).then(setInvitation).catch(e=>setError(e.message));},[token]);
 async function respond(decision:'accepted'|'declined'){
  setBusy(true);setError('');
  try{await api('/volunteer/'+encodeURIComponent(token)+'/respond',{decision});setInvitation(await api<PublicInvitation>('/volunteer/'+encodeURIComponent(token)));}
  catch(e){setError((e as Error).message);}finally{setBusy(false);}
 }
 return <div className="volunteer-page"><header><a className="wordmark" href="/">kind</a><span className="sample-label">Sample invitation</span></header><main className="volunteer-card">
  {error&&<p role="alert" className="error">{error}</p>}
  {!invitation&&!error&&<p>Opening your invitation…</p>}
  {invitation&&<><div className="volunteer-symbol">{invitation.status==='accepted'?<CheckCircle2 size={34}/>:<HeartHandshake size={34}/>}</div><p className="muted">{invitation.organization}</p><h1>{invitation.status==='accepted'?`You're on the team, ${invitation.name.split(' ')[0]}.`:invitation.status==='declined'?'Thanks for letting us know.':`A little help, ${invitation.name.split(' ')[0]}?`}</h1>
   <Status status={invitation.status}/><section className="invited-shift"><h2>{invitation.shift.title}</h2><ShiftTime shift={invitation.shift}/><ShiftDetails shift={invitation.shift}/></section>
   <p className="invitation-message">{invitation.message}</p>
   {invitation.status==='pending'?<><div className="button-row"><button className="primary" disabled={busy} onClick={()=>void respond('accepted')}>{busy?'Saving…':'I can help'}</button><button className="secondary" disabled={busy} onClick={()=>void respond('declined')}>Not this time</button></div><p className="small-muted">Accepting confirms you can attend the entire shift. It’s always okay to decline.</p></>:<p className="confirmation">{invitation.status==='accepted'?'Your place is confirmed and the coordinator’s roster has been updated.':invitation.status==='declined'?'Your response is saved. The coordinator can look for another volunteer.':'This invitation is no longer available. Please contact your coordinator.'}</p>}
   <p className="demo-disclosure">This is Kind’s local demo. The people and organization are fictional. Your response updates the sample roster.</p></>}
 </main><a className="back-link" href="/"><ArrowLeft size={16}/>Back to sample coordinator workspace</a></div>;
}
