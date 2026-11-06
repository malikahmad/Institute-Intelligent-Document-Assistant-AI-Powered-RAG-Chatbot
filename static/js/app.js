(() => {
const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";
const form = document.getElementById("chat-form");
if (form) {
 const history = document.getElementById("chat-history"), input = document.getElementById("question");
 let conversationId = null;
 function message(role, content, sources=[]) {
  const el=document.createElement("article"); el.className="message "+role;
  const title=document.createElement("b"); title.textContent=role==="user"?"You":"Institute Assistant";
  const p=document.createElement("p"); p.textContent=content; el.append(title,p);
  sources.forEach(s=>{const x=document.createElement("small");x.textContent=`[${s.marker}] ${s.document}, page ${s.page ?? "?"}`;el.append(x);});
  history.append(el);history.scrollTop=history.scrollHeight;
 }
 form.addEventListener("submit",async e=>{
  e.preventDefault();const question=input.value.trim();if(!question)return;
  message("user",question);input.value="";const button=form.querySelector("button");button.disabled=true;button.textContent="Thinking...";
  try {const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":csrf},body:JSON.stringify({question,conversation_id:conversationId})});
   const d=await r.json();if(!r.ok)throw new Error(d.error||"Request failed");conversationId=d.conversation_id;message("assistant",d.answer,d.sources||[]);
  } catch(err){message("assistant","Error: "+err.message);} finally{button.disabled=false;button.textContent="Send question";}
 });
}
const evalBtn=document.getElementById("run-evaluation");
if(evalBtn)evalBtn.addEventListener("click",async()=>{const out=document.getElementById("evaluation-output");evalBtn.disabled=true;out.textContent="Running...";
try{const r=await fetch("/api/admin/evaluation");const d=await r.json();if(!r.ok)throw new Error(d.error||"Failed");out.textContent=JSON.stringify(d,null,2);}catch(e){out.textContent=e.message;}finally{evalBtn.disabled=false;}});
})();
