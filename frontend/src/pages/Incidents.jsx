import {useEffect,useState} from "react";
import {Activity,Search,Filter,ArrowUpRight,Loader2,Plus} from "lucide-react";
import {Link} from "react-router-dom";
import Badge from "../components/common/Badge";
import {listIncidents,createIncident} from "../api/incidents";

export default function Incidents(){
  const [incidents,setIncidents]=useState([]),[search,setSearch]=useState(""),[loading,setLoading]=useState(true),[error,setError]=useState("");
  async function load(){
    setLoading(true);setError("");
    try{const data=await listIncidents();setIncidents(Array.isArray(data)?data:(data.incidents||data.items||[]))}
    catch(err){setError(err.response?.data?.detail||"Unable to load incidents.");}
    finally{setLoading(false)}
  }
  useEffect(()=>{load()},[]);
  async function create(){
    const title=window.prompt("Incident title");
    if(!title?.trim()) return;
    const description=window.prompt("Incident description");
    if(!description?.trim()) return;
    const service_name=window.prompt("Service name","payments-api")||"unknown-service";
    try{await createIncident({title,description,service_name,environment:"production"});await load()}
    catch(err){setError(err.response?.data?.detail||"Unable to create incident.")}
  }
  const rows=incidents.filter(i=>`${i.id} ${i.title} ${i.service_name}`.toLowerCase().includes(search.toLowerCase()));
  return <div className="page-stack"><div className="page-intro"><div><div className="eyebrow"><Activity size={13}/> OPERATIONS</div><h1>Incident management</h1><p>Monitor active incidents and use AI diagnosis for investigation.</p></div><button className="primary-btn" onClick={create}><Plus size={16}/> New incident</button></div><div className="toolbar panel"><div className="search-box"><Search size={17}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search incidents..."/></div><button className="secondary-btn" onClick={load}><Filter size={16}/> Refresh</button></div>{error&&<div className="error-box">{error}</div>}<div className="panel table-panel"><div className="table-head"><span>Incident</span><span>Service</span><span>Severity</span><span>Status</span><span>Created</span><span/></div>{loading?<div className="empty-mini"><Loader2 className="spin" size={24}/><span>Loading incidents...</span></div>:rows.length===0?<div className="empty-mini"><Activity size={24}/><strong>No incidents found</strong><span>Create an incident to begin investigation.</span></div>:rows.map(i=><Link className="incident-row" to={`/incidents/${i.id}`} key={i.id}><div><strong>INC-{i.id}</strong><span>{i.title}</span></div><span className="muted">{i.service_name}</span><Badge tone={(i.priority||i.severity||"medium").toLowerCase()}>{String(i.priority||i.severity||"MEDIUM").toUpperCase()}</Badge><Badge tone={i.status==="RESOLVED"?"success":"info"}>{i.status||"OPEN"}</Badge><span className="muted">{i.created_at?new Date(i.created_at).toLocaleString():"-"}</span><ArrowUpRight size={16}/></Link>)}</div></div>
}
