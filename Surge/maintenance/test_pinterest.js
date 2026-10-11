#!/usr/bin/env node
// Requirement fixtures for our own adapter. No upstream script is executed.
// Synthetic responses demonstrate behavior; these are not live account captures.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const cp = require("node:child_process");
const root = path.resolve(process.argv[2] || path.join(__dirname, "../.."));
const scriptPath = "Surge/Script/Kelee/Pinterest/remove-ads.js";
const source = fs.readFileSync(path.join(root, scriptPath), "utf8");
const home = "https://api.pinterest.com/v3/feeds/home/?bookmark=abc";
const related = "https://api.pinterest.com/v3/pins/123/related/modules/?source=pin";
let semanticCases = 0;
function invoke(body, request = {}, response = {}) {
  const calls = [];
  const req = {url: home, method: "GET", headers: {"X-Preserve": "request"}, ...request};
  const resp = {status: 200, headers: {"Content-Type": "application/json", "X-Preserve": "response"}, body, ...response};
  const before = JSON.stringify({req, resp});
  vm.runInNewContext(source, {$request: req, $response: resp, $done: value => calls.push(value)}, {timeout: 1000});
  assert.equal(calls.length, 1, "each invocation must finish exactly once");
  assert.equal(JSON.stringify({req, resp}), before, "the input request/response must remain unmodified");
  const result = JSON.parse(JSON.stringify(calls[0]));
  assert.ok(Object.keys(result).every(key => key === "body"), "do not change status/headers or abort");
  return result;
}
function unchanged(body, request = {}, response = {}) {
  assert.deepEqual(invoke(body, request, response), {}, "unchanged responses must retain their exact bytes");
  semanticCases++;
}
function rewritten(input, expected, request = {}) {
  const result = invoke(JSON.stringify(input), request);
  assert.ok(typeof result.body === "string", "an ad-containing array must be rewritten");
  assert.deepEqual(JSON.parse(result.body), expected);
  semanticCases++;
}
const organic = [
  {id: "organic-bool", is_promoted: false, images: {original: {url: "keep"}}},
  {id: "organic-string", is_promoted: "false"},
  {id: "missing-marker", title: "keep normal content"},
  {id: "null-marker", is_promoted: null},
  {id: "unknown-marker", is_promoted: "unknown"},
  {id: "numeric-marker", is_promoted: 0},
  {id: "numeric-one", is_promoted: 1},
  {id: "nested-marker", metadata: {is_promoted: true}},
  null, "keep-string", 7, ["keep-array"]
];
for (const url of [home, related]) {
  rewritten(
    {status: "success", data: [{id: "ad-bool", is_promoted: true}, ...organic, {id: "ad-string", is_promoted: "true"}],
     bookmark: "next-page", has_more: true, metadata: {request_id: "keep"}},
    {status: "success", data: organic, bookmark: "next-page", has_more: true, metadata: {request_id: "keep"}},
    {url}
  );
}
rewritten({data: [{is_promoted: true}, {is_promoted: "true"}], bookmark: "-end-"},
          {data: [], bookmark: "-end-"});
unchanged(' { "data" : [{"id":"regular","is_promoted":false},{"id":"unknown"}], "bookmark" : "exact" } ');
unchanged('{"data":[]}');
unchanged('{"data":{"pins":[{"id":"normal"}],"bookmark":"nested"}}');
unchanged('{"data":null,"status":"failure","message":"keep error"}');
unchanged('{"status":"failure","message":"reauth required"}');
unchanged('{"data":"unexpected string"}');
unchanged('[{"is_promoted":true}]');
unchanged('null');
unchanged('"json primitive"');
unchanged('invalid json');
unchanged('<html>upstream error</html>');
unchanged('');
unchanged(undefined);
unchanged(new Uint8Array([0, 1, 2]));
for (const status of [204, 301, 401, 403, 429, 500]) {
  unchanged('{"data":[{"is_promoted":true}],"message":"preserve non-success response"}', {}, {status, body: status === 204 ? "" : '{"data":[{"is_promoted":true}],"message":"preserve non-success response"}'});
}
unchanged('{"data":[{"is_promoted":true}]}', {method: "POST"});
for (const url of [
  "https://api.pinterest.com/v3/search/pins/?q=test",
  "https://api.pinterest.com/v3/users/me/?test=1",
  "https://api.pinterest.com/v3/oauth/token/?test=1",
  "https://api.pinterest.com/v3/pins/123/?test=1",
  "https://api.pinterest.com/v3/pins/not-a-number/related/modules/?test=1",
  "https://api.pinterest.com/v3/feeds/home/other/?test=1",
  "https://api.pinterest.com/v3/feeds/home/",
  "https://api.pinterest.com/v12/feeds/home/?test=1",
  "https://www.pinterest.com/",
  "https://i.pinimg.com/originals/image.jpg",
  "http://api.pinterest.com/v3/feeds/home/?test=1",
  "https://api.pinterest.com.evil.example/v3/feeds/home/?test=1"
]) unchanged('{"data":[{"is_promoted":true}]}', {url});
rewritten({data:[{is_promoted:true},{id:"keep",is_promoted:false}]},
          {data:[{id:"keep",is_promoted:false}]},
          {url:"HTTPS://API.PINTEREST.COM/v3/feeds/home/?test=1"});

// Equivalence with actual Loon jq on the shapes it explicitly handles.
const oldJq = '.data |= map(select(.is_promoted == false or .is_promoted == "false"))';
let originalCases = 0;
for (const data of [
  [{id:"a",is_promoted:false},{id:"b",is_promoted:true}],
  [{id:"a",is_promoted:"true"},{id:"b",is_promoted:"false"}],
  [{is_promoted:true},{is_promoted:"true"}]
]) {
  const payload = {status:"success",data,bookmark:"keep"};
  const expected = JSON.parse(cp.execFileSync("jq", ["-c", oldJq], {input:JSON.stringify(payload),encoding:"utf8"}));
  assert.deepEqual(JSON.parse(invoke(JSON.stringify(payload)).body), expected);
  originalCases++;
}
// Regression evidence: the old jq drops unidentified items and changes object data into an array.
const unknown = {data:[{id:"normal-no-marker"}],bookmark:"keep"};
assert.deepEqual(JSON.parse(cp.execFileSync("jq",["-c",oldJq],{input:JSON.stringify(unknown),encoding:"utf8"})),{data:[],bookmark:"keep"});
unchanged(JSON.stringify(unknown));
const objectData = {data:{first:{id:"normal",is_promoted:false},second:{id:"also-normal",is_promoted:false}}};
assert.ok(Array.isArray(JSON.parse(cp.execFileSync("jq",["-c",oldJq],{input:JSON.stringify(objectData),encoding:"utf8"})).data));
unchanged(JSON.stringify(objectData));
const unexpectedShape = {data:{pins:[{id:"normal"}],bookmark:"keep"}};
const legacyError = cp.spawnSync("jq",["-c",oldJq],{input:JSON.stringify(unexpectedShape),encoding:"utf8"});
assert.notEqual(legacyError.status,0,"the old unguarded jq cannot handle this response shape");
unchanged(JSON.stringify(unexpectedShape));
unchanged('{"status":"failure","data":[{"is_promoted":true}],"message":"preserve application error"}');
unchanged('{"data":[{"is_promoted":true},{"id":1234567890123456789,"is_promoted":false}],"bookmark":"keep"}');

// Installation and combined-module wiring; removing the old jq is part of the fix.
const moduleText = fs.readFileSync(path.join(root,"Surge/module/Kelee/Pinterest_remove_ads.sgmodule"),"utf8");
const bundleText = fs.readFileSync(path.join(root,"Surge/module/blockAds.module"),"utf8");
const scriptUrl = "https://raw.githubusercontent.com/WhiteSoulss/wool_scripts/main/" + scriptPath;
const parse = text => {
  const out = {}; let section = "";
  for (const raw of text.split(/\r?\n/)) {
    const row = raw.trim();
    if (/^\[[^\]]+\]$/.test(row)) { section=row.slice(1,-1); continue; }
    if (row && !/^[#;]/.test(row) && !row.startsWith("//")) (out[section] ||= []).push(row);
  }
  return out;
};
let urlCases = 0;
for (const text of [moduleText,bundleText]) {
  const sections = parse(text);
  assert.ok((sections.MITM || []).some(row => row.includes("api.pinterest.com")));
  assert.equal((sections["Body Rewrite"] || []).filter(row => row.includes("pinterest")).length,0);
  const row = (sections.Script || []).filter(row => row.includes(scriptUrl));
  assert.equal(row.length,1);
  assert.ok(row[0].includes("requires-body=true") && row[0].includes("max-size=1048576"));
  const nativePattern = row[0].match(/(?:^|,)\s*pattern=([^,]+)/)[1];
  assert.ok(nativePattern.startsWith("(?i)"));
  const regex = new RegExp(nativePattern.slice(4),"i");
  for (const [url,shouldMatch] of [[home,true],[related,true],["HTTPS://API.PINTEREST.COM/v3/feeds/home/?q=1",true],
    ["https://api.pinterest.com/v3/users/me/?q=1",false],["https://i.pinimg.com/image.jpg",false],
    ["https://api.pinterest.com/v3/feeds/home/other/?q=1",false],
    ["https://api.pinterest.com/v3/feeds/home/",false]]) {
    assert.equal(regex.test(url),shouldMatch,url);
    urlCases++;
  }
}
console.log(JSON.stringify({pinterest_semantic_cases:semanticCases,pinterest_original_semantics_cases:originalCases,pinterest_module_url_cases:urlCases}));
