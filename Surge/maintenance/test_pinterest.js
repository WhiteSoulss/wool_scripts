#!/usr/bin/env node
// Tests for our handwritten native mapping, using the actual archived LPX.
// jq fixtures are synthetic and do not run Surge or authenticate to Pinterest.
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),cp=require("node:child_process");
const root=path.resolve(process.argv[2]||path.join(__dirname,"../.."));
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const source=read("Surge/Kelee-review/loon-original/Pinterest_remove_ads.lpx");
const original=source.split(/\r?\n/).filter(x=>x.startsWith("response if ")).map(row=>{
  const m=row.match(/^response if \$\{url\} ~= \/(.*)\/i then response\.json\.jq\((.*)\)$/);
  assert.ok(m,"read the actual inline Loon action");
  return {pattern:m[1],regex:new RegExp(m[1],"i"),expression:JSON.parse(m[2])};
});
assert.equal(original.length,2);
const expression='.data |= map(select(.is_promoted == false or .is_promoted == "false"))';
for(const o of original)assert.equal(o.expression,expression);
function parse(text){
  const out={};let key="";
  for(const raw of text.split(/\r?\n/)){
    const row=raw.trim();
    if(/^\[[^\]]+\]$/.test(row)){key=row.slice(1,-1);continue;}
    if(row&&!/^(?:#|;|\/\/)/.test(row))(out[key]||=[]).push(row);
  }
  return out;
}
const nativeFiles=["Surge/module/Kelee/Pinterest_remove_ads.sgmodule","Surge/module/blockAds.module"];
const configurations=nativeFiles.map(file=>{
  const text=read(file),sections=parse(text);
  assert.ok(!text.includes("Surge/Script/Kelee/Pinterest/remove-ads.js"),"remove obsolete adapter references");
  assert.ok(!(sections.Script||[]).some(x=>/pinterest/i.test(x)),"no Pinterest response script");
  const rows=(sections["Body Rewrite"]||[]).filter(x=>/pinterest/i.test(x)).map(row=>{
    const m=row.match(/^http-response-jq\s+(\S+)\s+'(.*)'$/);
    assert.ok(m,"native Surge JQ row syntax"); assert.ok(m[1].startsWith("(?i)"));
    return {pattern:m[1],regex:new RegExp(m[1].slice(4),"i"),expression:m[2]};
  });
  assert.equal(rows.length,2,"exactly the two original actions");
  rows.forEach((x,i)=>assert.equal(x.expression,original[i].expression,"the original jq expression must be unchanged"));
  const hostRow=(sections.MITM||[]).find(x=>/^hostname\s*=/.test(x));
  assert.ok(hostRow&&hostRow.includes("%APPEND%"));
  const hosts=hostRow.replace(/^hostname\s*=\s*%APPEND%\s*/,"").split(",").map(x=>x.trim());
  assert.equal(hosts.filter(x=>x==="api.pinterest.com").length,1);
  if(file.includes("/Kelee/"))assert.deepEqual(hosts,["api.pinterest.com"]);
  return {file,rows};
});
assert.ok(!fs.existsSync(path.join(root,"Surge/Script/Kelee/Pinterest/remove-ads.js")),"delete the superseded adapter");
const fixtures=[
  ["https://api.pinterest.com/v3/feeds/home/?bookmark=abc",[true,false]],
  ["https://api.pinterest.com/v3/pins/123/related/modules/?source=pin",[false,true]],
  ["HTTPS://API.PINTEREST.COM/V3/FEEDS/HOME/?q=1",[true,false]],
  ["HTTPS://API.PINTEREST.COM/V3/PINS/001/RELATED/MODULES/?q=1",[false,true]],
  ["https://api.pinterest.com/v0/feeds/home/?",[true,false]],
  ["https://api.pinterest.com/v9/pins/0/related/modules/?",[false,true]],
  ["https://api.pinterest.com/v3/feeds/home/",[false,false]],
  ["https://api.pinterest.com/v3/pins/123/related/modules/",[false,false]],
  ["https://api.pinterest.com/v12/feeds/home/?q=1",[false,false]],
  ["https://api.pinterest.com/v12/pins/123/related/modules/?q=1",[false,false]],
  ["http://api.pinterest.com/v3/feeds/home/?q=1",[false,false]],
  ["https://api.pinterest.com/v3/feeds/home/other/?q=1",[false,false]],
  ["https://api.pinterest.com/v3/pins/not-a-number/related/modules/?q=1",[false,false]],
  ["https://api.pinterest.com/v3/pins/123/?q=1",[false,false]],
  ["https://api.pinterest.com/v3/search/pins/?q=test",[false,false]],
  ["https://api.pinterest.com/v3/users/me/?q=1",[false,false]],
  ["https://api.pinterest.com/v3/oauth/token/?q=1",[false,false]],
  ["https://www.pinterest.com/",[false,false]],
  ["https://i.pinimg.com/image.jpg",[false,false]],
  ["https://api.pinterest.com.evil.example/v3/feeds/home/?q=1",[false,false]],
  ["https://api.pinterest.com:443/v3/feeds/home/?q=1",[false,false]]
];
let urlCases=0;
for(const [url,want]of fixtures){
  assert.deepEqual(original.map(x=>x.regex.test(url)),want,"source scope independently expected: "+url);
  for(const cfg of configurations){
    assert.deepEqual(cfg.rows.map(x=>x.regex.test(url)),want,cfg.file+": "+url);
    urlCases++;
  }
}
const ordinary=[
 {id:"boolean-false",is_promoted:false,nested:{is_promoted:true,keep:1}},
 {id:"string-false",is_promoted:"false"}
];
const dropped=[
 {id:"ad",is_promoted:true},{id:"ad-string",is_promoted:"true"},
 {id:"missing"},{id:"null",is_promoted:null},{id:"zero",is_promoted:0},
 {id:"one",is_promoted:1},{id:"unknown",is_promoted:"unknown"},
 {id:"case-different",is_promoted:"False"},{id:"empty",is_promoted:""},
 {id:"object",is_promoted:{}},{id:"array",is_promoted:[]},null
];
const cases=[
 {input:{data:[...dropped,...ordinary],bookmark:"next",status:"success",has_more:true},expected:{data:ordinary,bookmark:"next",status:"success",has_more:true}},
 {input:{data:ordinary,bookmark:"same"},expected:{data:ordinary,bookmark:"same"}},
 {input:{data:dropped,bookmark:"next"},expected:{data:[],bookmark:"next"}},
 {input:{data:[],bookmark:"end"},expected:{data:[],bookmark:"end"}},
 {input:{data:[ordinary[1],dropped[0],ordinary[0]],extra:{keep:true}},expected:{data:[ordinary[1],ordinary[0]],extra:{keep:true}}},
 {input:{data:[{id:"12345678901234567890",is_promoted:false},{id:"ads",is_promoted:true}]},expected:{data:[{id:"12345678901234567890",is_promoted:false}]}},
 {input:{status:"failure",data:[ordinary[0],dropped[0]],message:"retain"},expected:{status:"failure",data:[ordinary[0]],message:"retain"}},
 // Native jq's behavior on object-shaped data is preserved, not replaced by custom JS guards.
 {input:{data:{first:ordinary[0],ad:dropped[0],second:ordinary[1]},bookmark:"keep"},expected:{data:ordinary,bookmark:"keep"}}
];
function execute(expr,input){
 return cp.spawnSync("jq",["-c",expr],{input:typeof input==="string"?input:JSON.stringify(input),encoding:"utf8",timeout:2000});
}
let semanticCases=0,originalCases=0;
for(const item of cases){
 for(const o of original){
   const result=execute(o.expression,item.input);assert.equal(result.status,0,result.stderr);
   assert.deepEqual(JSON.parse(result.stdout),item.expected);originalCases++;
 }
 for(const cfg of configurations)for(const row of cfg.rows){
   const result=execute(row.expression,item.input);assert.equal(result.status,0,result.stderr);
   assert.deepEqual(JSON.parse(result.stdout),item.expected);semanticCases++;
 }
}
const invalidInputs=[
 '{"status":"failure","message":"no data"}','{"data":null}','{"data":"unexpected"}',
 '{"data":{"pins":[{"id":"normal"}],"bookmark":"keep"}}','<html>error</html>','invalid JSON'
];
let errorCases=0;
for(const input of invalidInputs){
 const expected=execute(original[0].expression,input);
 assert.notEqual(expected.status,0,"source jq rejects this shape");
 for(const cfg of configurations)for(const row of cfg.rows){
   const result=execute(row.expression,input);
   assert.equal(result.status,expected.status,"preserve jq error behavior");errorCases++;
 }
}
// Authorization explicitly supersedes the temporary deployment pause, not client evidence.
const manifest=JSON.parse(read("Surge/Kelee-review/manifest.json"));
const entry=manifest.modules.find(x=>x.filename==="Pinterest_remove_ads.sgmodule");
assert.equal(entry.deployment.enabled,true);
assert.equal(entry.deployment.client_runtime_tested,false);
const pending=JSON.parse(read("Surge/Kelee-review/pinterest-pending-review.json"));
assert.equal(pending.status,"native-rewrite-awaiting-client-confirmation");
assert.equal(pending.manual_source_review_complete,true);
assert.ok(pending.reenable_authorization.includes("原版"));
assert.equal(pending.client_success_confirmed,false);
assert.deepEqual(entry.actions,{"Body Rewrite":2});
assert.ok(!manifest.resources.some(x=>x.path==="Surge/Script/Kelee/Pinterest/remove-ads.js"));
console.log(JSON.stringify({
 pinterest_semantic_cases:semanticCases,pinterest_original_semantics_cases:originalCases,
 pinterest_module_url_cases:urlCases,pinterest_jq_error_equivalence_cases:errorCases,
 pinterest_native_modules_checked:configurations.length
}));
