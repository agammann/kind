export async function api<T>(path:string,body?:unknown):Promise<T> {
  const response=await fetch('/api'+path,{method:body===undefined?'GET':'POST',credentials:'same-origin',headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
  const result=await response.json();
  if(!response.ok) throw new Error(typeof result.detail==='string'?result.detail:'Something went wrong. Please try again.');
  return result as T;
}
export function dateLabel(value:string,options:Intl.DateTimeFormatOptions={month:'short',day:'numeric'}) {
  return new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',...options}).format(new Date(value));
}
export function timeRange(start:string,end:string) {
  return `${dateLabel(start,{hour:'numeric',minute:'2-digit'})} – ${dateLabel(end,{hour:'numeric',minute:'2-digit',timeZoneName:'short'})}`;
}
export function initials(name:string){return name.split(' ').map(n=>n[0]).join('').slice(0,2);}
