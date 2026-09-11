"""Local demo server. Bind only to loopback; production identity/hosting is a separate step."""
import asyncio
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .store import Store, WorkflowError
from .agent import prepare


def create_app(store=None, *, auth=None, public_host=None, jobs=None):
    if (auth is None) != (public_host is None):
        raise ValueError('Hosted mode requires both authentication and a trusted host.')
    workspace=store or Store()
    session_token=secrets.token_urlsafe(32)
    agent_lock=asyncio.Lock()

    @asynccontextmanager
    async def lifespan(app):
        async def watch():
            while True:
                await asyncio.to_thread(workspace.scan)
                await asyncio.sleep(30)
        task=asyncio.create_task(watch())
        yield
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass

    app=FastAPI(title='Kind',lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=[public_host] if public_host else ['127.0.0.1','localhost','testserver'])

    @app.middleware('http')
    async def local_boundary(request: Request, call_next):
        origin=request.headers.get('origin')
        if request.url.path.startswith('/api'):
            allowed={'http://127.0.0.1:5173','http://localhost:5173','http://127.0.0.1:8000','http://localhost:8000','http://testserver'}
            if public_host: allowed={f'https://{public_host}'}
            if (origin and origin not in allowed) or request.headers.get('sec-fetch-site')=='cross-site':
                return JSONResponse({'detail':'Cross-site API access is not allowed.'},status_code=403)
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        if public_host: response.headers['Strict-Transport-Security']='max-age=31536000'
        return response

    @app.exception_handler(WorkflowError)
    async def workflow_error(request,exc): return JSONResponse({'detail':exc.message},status_code=exc.status)

    def coordinator(request:Request):
        value=request.cookies.get('kind_coordinator','')
        if auth:
            if not auth.valid(value): raise WorkflowError('Enter the coordinator access code to open this demo.',401)
            return
        if not secrets.compare_digest(value,session_token): raise WorkflowError('Open the coordinator workspace to start a local session.',401)

    class Login(BaseModel): access_code: str=Field(default='',max_length=256)

    @app.post('/api/session')
    def session(request: Request,response: Response,body: Login=Login()):
        if auth:
            if auth.valid(request.cookies.get('kind_coordinator','')):
                return {'mode':'hosted_sample_workspace'}
            if not auth.accepts(body.access_code):
                raise WorkflowError('Enter the coordinator access code to open this demo.',401)
        response.set_cookie('kind_coordinator',auth.issue() if auth else session_token,httponly=True,
            secure=bool(auth),samesite='strict',max_age=43200)
        return {'mode':'hosted_sample_workspace' if auth else 'local_sample_workspace'}

    @app.post('/api/logout')
    def logout(response: Response):
        response.delete_cookie('kind_coordinator',secure=bool(auth),httponly=True,samesite='strict')
        return {'status':'signed_out'}

    @app.get('/api/health')
    def health(): return {'status':'ok','sample_data':True,'bedrock_configured':bool(os.getenv('KIND_BEDROCK_MODEL_ID'))}

    @app.get('/api/workspace',dependencies=[Depends(coordinator)])
    def get_workspace():
        if jobs: workspace.scan()
        state=workspace.read()
        state={k:v for k,v in state.items() if not k.startswith('_')}
        state['hosted']=bool(auth)
        state['bedrock_configured']=bool(os.getenv('KIND_BEDROCK_MODEL_ID'))
        return state

    @app.get('/api/shifts/{shift_id}/candidates',dependencies=[Depends(coordinator)])
    def candidates(shift_id:str): return workspace.candidates(shift_id)

    class RestartSample(BaseModel): confirm: Literal['restart fictional sample']

    @app.post('/api/sample/restart',dependencies=[Depends(coordinator)])
    async def restart_sample(body:RestartSample):
        if agent_lock.locked(): raise WorkflowError('Wait for preparation to finish before restarting the sample.')
        async with agent_lock:
            return await asyncio.to_thread(workspace.restart_sample)

    class PrepareRequest(BaseModel): mode: Literal['rules','bedrock']='rules'

    @app.post('/api/shifts/{shift_id}/prepare',dependencies=[Depends(coordinator)])
    async def prepare_shift(shift_id:str,body:PrepareRequest):
        if jobs and body.mode=='bedrock':
            return JSONResponse(await asyncio.to_thread(jobs.start,shift_id),status_code=202)
        if agent_lock.locked(): raise WorkflowError('An invitation is already being prepared. Please wait.')
        async with agent_lock:
            return await asyncio.to_thread(prepare,workspace,shift_id,body.mode)

    @app.get('/api/jobs/{job_id}',dependencies=[Depends(coordinator)])
    def get_job(job_id:str):
        if not jobs: raise WorkflowError('Background jobs are not enabled locally.',404)
        return jobs.get(job_id)

    class Approval(BaseModel): message: str=Field(min_length=1,max_length=2000)

    @app.post('/api/invitations/{invitation_id}/approve',dependencies=[Depends(coordinator)])
    def approve(invitation_id:str,body:Approval): return workspace.approve(invitation_id,body.message)

    @app.post('/api/invitations/{invitation_id}/cancel',dependencies=[Depends(coordinator)])
    def cancel(invitation_id:str):
        workspace.cancel_invitation(invitation_id)
        return {'status':'cancelled'}

    class Cancellation(BaseModel): volunteer_id:str

    @app.post('/api/shifts/{shift_id}/cancel-assignment',dependencies=[Depends(coordinator)])
    def cancel_assignment(shift_id:str,body:Cancellation):
        workspace.cancel_assignment(shift_id,body.volunteer_id)
        workspace.scan()
        return {'status':'cancelled'}

    @app.post('/api/scan',dependencies=[Depends(coordinator)])
    def scan(): return workspace.scan()

    @app.get('/api/volunteer/{token}')
    def public_invitation(token:str): return workspace.public_invitation(token)

    class VolunteerResponse(BaseModel): decision: Literal['accepted','declined']

    @app.post('/api/volunteer/{token}/respond')
    def respond(token:str,body:VolunteerResponse): return workspace.respond(token,body.decision)

    dist=Path(__file__).resolve().parent.parent/'dist'
    if (dist/'assets').exists(): app.mount('/assets',StaticFiles(directory=dist/'assets'),name='assets')

    @app.get('/{path:path}')
    def frontend(path:str):
        if path.startswith('api/'): raise WorkflowError('Endpoint not found.',404)
        if not (dist/'index.html').exists(): raise WorkflowError('Build the frontend or use the Vite preview.',503)
        return FileResponse(dist/'index.html')

    return app


app=None if os.getenv('KIND_HOSTED')=='1' else create_app()
