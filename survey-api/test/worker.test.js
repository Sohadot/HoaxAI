import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { Script } from 'node:vm';
import worker from '../src/index.js';

const url='https://hoax.ai/survey/api/';
const readyEnv={
  DB:{prepare(query){assert.match(query,/INSERT OR IGNORE INTO survey_responses/);return {bind(...args){return {async run(){assert.equal(args.length,7);return {success:true};}};}};}},
  ALLOWED_ORIGIN:'https://hoax.ai',TURNSTILE_SECRET:'test-secret',TURNSTILE_SITEKEY:'site-key'
};
const answer={
 request_id:'12345678-1234-4234-8234-123456789abc',
 q1:'detector',q2:'evidence',q3:'sources',q4:'conditional',q5:'Useful feedback',
 referral:'direct',turnstile_token:'valid-token-string-for-testing'
};
const req=(body=answer,origin='https://hoax.ai')=>new Request(url+'submit',{
 method:'POST',headers:{'Origin':origin,'Content-Type':'application/json'},body:JSON.stringify(body)
});

test('survey browser script compiles as JavaScript',()=>{
 const html=readFileSync(resolve(import.meta.dirname,'../../survey/index.html'),'utf8');
 const match=html.match(/<script>([\s\S]*?)<\/script>/);
 assert.ok(match,'inline form controller script present');
 assert.doesNotThrow(()=>new Script(match[1]));
 assert.match(html,/noindex,nofollow/);
 assert.match(html,/type="radio" name="q1"/);
 assert.match(html,/id="done"/);
});

test('service fails closed before D1 and Turnstile setup',async()=>{
 const r=await worker.fetch(new Request(url+'status'),{});
 assert.equal(r.status,503);
 assert.equal((await r.json()).ready,false);
});

test('status exposes only public sitekey on ready service',async()=>{
 const r=await worker.fetch(new Request(url+'status'),readyEnv);
 assert.equal(r.status,200);
 const v=await r.json();
 assert.equal(v.sitekey,'site-key');
 assert.equal(JSON.stringify(v).includes('test-secret'),false);
});

test('cross-origin submissions rejected',async()=>{
 const r=await worker.fetch(req(answer,'https://evil.example'),readyEnv);
 assert.equal(r.status,403);
});

test('invalid answers rejected without calling challenge service',async()=>{
 const r=await worker.fetch(req({...answer,q1:'unsupported'}),readyEnv);
 assert.equal(r.status,400);
});

test('Turnstile rejects challenge with unexpected hostname',async()=>{
 const original=globalThis.fetch;
 globalThis.fetch=async()=>Response.json({success:true,hostname:'other.example',action:'hoax_survey'});
 try{const r=await worker.fetch(req(),readyEnv);assert.equal(r.status,403);}
 finally{globalThis.fetch=original;}
});

test('valid survey saved only after server validation',async()=>{
 const original=globalThis.fetch;
 let verified=false, persisted=false;
 const env={...readyEnv,DB:{prepare(){return {bind(...values){assert.equal(values[0],answer.request_id);return {async run(){persisted=true;assert.equal(verified,true);}};}};}}};
 globalThis.fetch=async(input,options)=>{
   assert.match(input,/siteverify/);
   assert.equal(options.method,'POST');
   verified=true;
   return Response.json({success:true,hostname:'hoax.ai',action:'hoax_survey'});
 };
 try{
  const r=await worker.fetch(req(),env);
  assert.equal(r.status,200);assert.equal((await r.json()).received,true);
  assert.equal(persisted,true);
 }finally{globalThis.fetch=original;}
});
