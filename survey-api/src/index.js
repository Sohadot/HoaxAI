// Hoax.ai public interpretation survey: private submissions on Cloudflare D1.
// This Worker must be mounted ONLY at hoax.ai/survey/api/*.
// No credentials or results belong in this public repository.
const RESP_HEADERS={
  'Content-Type':'application/json; charset=utf-8',
  'Cache-Control':'no-store',
  'X-Content-Type-Options':'nosniff',
  'Referrer-Policy':'no-referrer',
  'Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'"
};
const OPTIONS={
  q1:['detector','guidance','news','other','unsure'],
  q2:['evidence','detector','reporting','unsure'],
  q3:['checklist','sources','synthetic','gaps'],
  q4:['regular','occasional','conditional','unlikely'],
  referral:['rick','discord','direct','other']
};
function json(body,status=200){return new Response(JSON.stringify(body),{status,headers:RESP_HEADERS});}
const good=(value,choices)=>typeof value==='string'&&choices.includes(value);
export default {
 async fetch(request,env){
  const url=new URL(request.url);
  const path=url.pathname;
  const ready=Boolean(env.DB&&env.TURNSTILE_SECRET&&env.TURNSTILE_SITEKEY&&env.ALLOWED_ORIGIN);
  if(path==='/survey/api/status'&&request.method==='GET'){
   return ready?json({ready:true,sitekey:env.TURNSTILE_SITEKEY}):json({ready:false},503);
  }
  if(path!=='/survey/api/submit'||request.method!=='POST')return json({error:'Not found'},404);
  if(!ready)return json({error:'Survey unavailable'},503);
  // This is a same-origin-only write endpoint. Never enable wildcard CORS.
  if(request.headers.get('Origin')!==env.ALLOWED_ORIGIN)return json({error:'Forbidden origin'},403);
  const ctype=request.headers.get('Content-Type')||'';
  if(!ctype.toLowerCase().startsWith('application/json'))return json({error:'Expected JSON'},415);
  if(Number(request.headers.get('Content-Length')||0)>4096)return json({error:'Payload too large'},413);
  let body;
  try{
   const raw=await request.text();
   if(raw.length>4096)return json({error:'Payload too large'},413);
   body=JSON.parse(raw);
  }catch(e){return json({error:'Malformed JSON'},400);}
  if(!body||typeof body!=='object'||Array.isArray(body))return json({error:'Malformed submission'},400);
  if(typeof body.request_id!=='string'||!/^[a-f0-9-]{36}$/i.test(body.request_id))return json({error:'Invalid request ID'},400);
  if(!good(body.q1,OPTIONS.q1)||!good(body.q2,OPTIONS.q2)||!good(body.q3,OPTIONS.q3)||!good(body.q4,OPTIONS.q4)||!good(body.referral,OPTIONS.referral)){
   return json({error:'Invalid answers'},400);
  }
  if(typeof body.q5!=='string'||body.q5.length>500||/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(body.q5)){
   return json({error:'Invalid comment'},400);
  }
  if(typeof body.turnstile_token!=='string'||body.turnstile_token.length<20||body.turnstile_token.length>2048){
   return json({error:'Verification required'},400);
  }
  // Verify server-side. A public site key is not sufficient to prevent spam.
  let verified;
  try{
   const params=new URLSearchParams({secret:env.TURNSTILE_SECRET,response:body.turnstile_token});
   const result=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{
    method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:params
   });
   if(!result.ok)return json({error:'Verification temporarily unavailable'},503);
   verified=await result.json();
  }catch(e){return json({error:'Verification temporarily unavailable'},503);}
  if(verified.success!==true||verified.hostname!=='hoax.ai'||verified.action!=='hoax_survey'){
   return json({error:'Verification failed'},403);
  }
  // Anonymity by design: never persist IP, UA, email, cookie or analytics ID.
  try{
   await env.DB.prepare(
    'INSERT OR IGNORE INTO survey_responses (request_id,q1,q2,q3,q4,q5,referral) VALUES (?,?,?,?,?,?,?)'
   ).bind(body.request_id,body.q1,body.q2,body.q3,body.q4,body.q5,body.referral).run();
   return json({received:true});
  }catch(e){return json({error:'Unable to save response'},503);}
 }
};
