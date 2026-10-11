"use strict";
(async()=>{
 const get=id=>document.querySelector("[data-"+id+"]");
 const records=get("records"),date=get("release-date"),status=get("integrity");
 if(!records||!date||!status)return;
 function fail(){records.textContent="Unavailable";date.textContent="Unavailable";status.textContent="Not verified"}
 try{
  const names=["evidence.json","sources.json","release-manifest.json"];
  const files=await Promise.all(names.map(async n=>{const response=await fetch("../data/current/"+n,{cache:"no-store",credentials:"omit"});if(!response.ok)throw Error("HTTP "+response.status);const body=await response.arrayBuffer();return {name:n,body,data:JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(body))}}));
  const [evidence,sources,manifest]=files;
  if(!crypto.subtle||!manifest.data.files)throw Error("Integrity unavailable");
  for(const file of [evidence,sources]) {
   const bytes=await crypto.subtle.digest("SHA-256",file.body);
   const checksum=[...new Uint8Array(bytes)].map(b=>b.toString(16).padStart(2,"0")).join("");
   if(checksum!==manifest.data.files[file.name]?.sha256)throw Error("Bad SHA256: "+file.name);
  }
  if(!Array.isArray(evidence.data.records)||!Array.isArray(sources.data.sources)||manifest.data.record_count!==evidence.data.records.length||evidence.data.generated_at!==manifest.data.generated_at)throw Error("Inconsistent manifest");
  records.textContent=String(evidence.data.records.length);
  date.textContent=new Intl.DateTimeFormat("en-GB",{dateStyle:"medium",timeZone:"UTC"}).format(new Date(evidence.data.generated_at));
  status.textContent="SHA-256 verified";
 }catch(err){console.error("Release verification failed",err);fail()}
})();