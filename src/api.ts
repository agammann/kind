export class ApiError extends Error {
  constructor(message:string,public status:number){super(message);}
}
export async function api<T>(path:string,body?:unknown):Promise<T> {
  const response=await fetch('/api'+path,{method:body===undefined?'GET':'POST',credentials:'same-origin',headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
  const result=await response.json();
  if(!response.ok) throw new ApiError(typeof result.detail==='string'?result.detail:'Something went wrong. Please try again.',response.status);
  if(response.status===202 && result.job_id){
    for(let attempt=0;attempt<205;attempt++){
      await new Promise(resolve=>setTimeout(resolve,2000));
      const job=await api<{status:string;result?:T;error?:string}>(`/jobs/${encodeURIComponent(result.job_id)}`);
      if(job.status==='complete')return job.result as T;
      if(job.status==='failed')throw new Error(job.error||'The worker could not complete this run.');
    }
    throw new Error('Preparation is taking longer than expected. Check saved drafts before trying again.');
  }
  return result as T;
}
export function dateLabel(value:string,options:Intl.DateTimeFormatOptions={month:'short',day:'numeric'}) {
  return new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',...options}).format(new Date(value));
}
export function timeRange(start:string,end:string) {
  return `${dateLabel(start,{hour:'numeric',minute:'2-digit'})} – ${dateLabel(end,{hour:'numeric',minute:'2-digit',timeZoneName:'short'})}`;
}
export function initials(name:string){return name.split(' ').map(n=>n[0]).join('').slice(0,2);}
