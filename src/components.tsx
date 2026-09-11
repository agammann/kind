import {useEffect,useRef,type ReactNode} from 'react';
import {AlertTriangle,Check,Clock3, X,LockKeyhole, MapPin,ShieldCheck} from 'lucide-react';
import {dateLabel,initials,timeRange} from './api';
import type {Activity,Shift} from './types';

export function Status({status}:{status:string}){
 const positive=['covered','accepted'].includes(status), waiting=['pending','awaiting'].includes(status);
 const names:Record<string,string>={covered:'Covered',open:'Needs coverage',pending:'Awaiting reply',awaiting:'Awaiting reply',draft:'Needs approval',accepted:'Accepted',declined:'Declined',filled:'Shift filled',cancelled:'Cancelled',expired:'Expired'};
 const Icon=positive?Check:waiting?Clock3:AlertTriangle;
 return <span className={`status ${positive?'positive':waiting?'waiting':['open','draft'].includes(status)?'warning':'neutral'}`}><Icon size={15}/>{names[status]||status}</span>;
}
export function Avatar({name,small=false}:{name:string;small?:boolean}){return <span className={`avatar ${small?'small':''}`}>{initials(name)}</span>;}
export function ApprovalNote(){return <p className="approval-note"><LockKeyhole size={16}/>You approve every invitation.</p>;}
export function ShiftDetails({shift}:{shift:Omit<Shift,'id'|'required'|'assigned'>}){return <div className="shift-details"><div><MapPin/><span><strong>Location</strong>{shift.location}</span></div><div><ShieldCheck/><span><strong>Required qualification</strong>{shift.qualification}</span></div></div>;}
export function ActivityList({items}:{items:Activity[]}){return <div className="activity-list">{items.length?items.map(item=><div className="activity-row" key={item.id}><span className="event-icon">{item.title==='Shift covered'?<Check size={17}/>:<Clock3 size={17}/>}</span><div><strong>{item.title}</strong><p>{item.detail}</p></div><time dateTime={item.at}>{dateLabel(item.at,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'})}</time></div>):<p className="empty">No activity yet.</p>}</div>;}
export function Dialog({title,onClose,children}:{title:string;onClose:()=>void;children:ReactNode}){
 const ref=useRef<HTMLDialogElement>(null);
 useEffect(()=>{const element=ref.current!;element.showModal();return()=>element.close();},[]);
 return <dialog ref={ref} onCancel={onClose} aria-labelledby="dialog-title"><div className="dialog-head"><h2 id="dialog-title">{title}</h2><button className="icon-button" onClick={onClose} aria-label="Close dialog"><X/></button></div>{children}</dialog>;
}
export function ShiftTime({shift}:{shift:Omit<Shift,'id'|'required'|'assigned'>}){return <p className="muted">{dateLabel(shift.start,{weekday:'long',month:'long',day:'numeric'})} · {timeRange(shift.start,shift.end)}</p>;}
