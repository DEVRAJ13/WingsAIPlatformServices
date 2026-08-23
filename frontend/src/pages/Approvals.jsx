import {useEffect,useState} from "react";
import {CheckCircle2,XCircle,ShieldCheck,Play,RefreshCw,Loader2} from "lucide-react";
import Badge from "../components/common/Badge";
import {listApprovals,decideApproval,executeApproval} from "../api/approvals";

function normalize(item) {
  const a = item?.approval || item;
  return {
    ...a,
    id: a.id,
    tool: a.tool_name || a.tool || "unknown",
    reason: a.reason || "",
    status: String(a.status || "PENDING").toUpperCase(),
  };
}

export default function Approvals(){
  const [items,setItems]=useState([]),[busy,setBusy]=useState(null),[error,setError]=useState("");

  async function load(){
    setError("");
    try{
      const data=await listApprovals();
      const rows=Array.isArray(data)?data:(data.approvals||data.items||[]);
      setItems(rows.map(normalize));
    }catch(err){
      setError(err.response?.data?.detail||"Unable to load approvals.");
    }
  }
  useEffect(()=>{load()},[]);

  async function decide(id,status){
    setBusy(`${id}:${status}`);
    setError("");
    try{
      const data=await decideApproval(id,{decision:status});
      const updated=normalize(data);
      setItems(x=>x.map(a=>a.id===id?{...a,...updated,status}:a));
    }catch(err){setError(err.response?.data?.detail||"Approval decision failed.");}
    finally{setBusy(null)}
  }

  async function execute(id){
    setBusy(`${id}:EXECUTE`);
    setError("");
    try{
      const data=await executeApproval(id);
      const updated=data.execution||data;
      setItems(x=>x.map(a=>a.id===id?{...a,status:updated.status||"EXECUTED"}:a));
    }catch(err){setError(err.response?.data?.detail||"Tool execution failed.");}
    finally{setBusy(null)}
  }

  return <div className="page-stack">
    <div className="page-intro"><div><div className="eyebrow"><ShieldCheck size={13}/> HUMAN-IN-THE-LOOP</div><h1>Approval center</h1><p>Review AI-recommended actions before tools can execute.</p></div><button className="secondary-btn" onClick={load} disabled={!!busy}><RefreshCw size={16}/> Refresh</button></div>
    <div className="approval-banner"><ShieldCheck size={21}/><div><strong>Execution gate is active</strong><span>Only explicitly approved requests can execute operational tools.</span></div></div>
    {error&&<div className="error-box">{error}</div>}
    <div className="panel table-panel">
      {items.length===0&&!error&&<div className="empty-mini"><ShieldCheck size={24}/><strong>No approval requests</strong><span>New AI-recommended actions will appear here.</span></div>}
      {items.map(a=><div className="approval-row" key={a.id}><div className="approval-id">#{a.id}</div><div className="approval-info"><strong>{a.tool}</strong><span>{a.reason}</span><small>Approval request</small></div><Badge tone={a.status==="APPROVED"||a.status==="EXECUTED"?"success":a.status==="REJECTED"?"danger":"pending"}>{a.status}</Badge><div className="approval-actions">{a.status==="PENDING"&&<><button disabled={!!busy} className="approve-btn" onClick={()=>decide(a.id,"APPROVED")}>{busy===`${a.id}:APPROVED`?<Loader2 className="spin" size={15}/>:<CheckCircle2 size={15}/>} Approve</button><button disabled={!!busy} className="reject-btn" onClick={()=>decide(a.id,"REJECTED")}>{busy===`${a.id}:REJECTED`?<Loader2 className="spin" size={15}/>:<XCircle size={15}/>} Reject</button></>}{a.status==="APPROVED"&&<button disabled={!!busy} className="approve-btn" onClick={()=>execute(a.id)}>{busy===`${a.id}:EXECUTE`?<Loader2 className="spin" size={15}/>:<Play size={15}/>} Execute</button>}</div></div>)}
    </div>
    <div className="panel"><div className="panel-head"><div><h2>Safety principles</h2><p>WINGS separates recommendation from execution.</p></div></div><div className="principles">{["AI recommends","Human approves","Tool executes","Audit records"].map((x,i)=><div key={x}><strong>0{i+1}</strong><span>{x}</span></div>)}</div></div>
  </div>
}
