import { useState } from "react";
import { FileText, Upload, CheckCircle2, Loader2 } from "lucide-react";
import { createDocument } from "../api/documents";
export default function Documents() {
  const [title, setTitle] = useState(""),
    [content, setContent] = useState(""),
    [result, setResult] = useState(null),
    [loading, setLoading] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      setResult(await createDocument({ title, content }));
      setTitle("");
      setContent("");
    } catch (err) {
      setResult({
        error: err.response?.data?.detail || "Document ingestion failed.",
      });
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="page-stack">
      <div className="page-intro">
        <div>
          <div className="eyebrow">
            <FileText size={13} /> KNOWLEDGE INGESTION
          </div>
          <h1>Documents</h1>
          <p>Add enterprise documents to the WINGS semantic knowledge base.</p>
        </div>
      </div>
      <div className="two-column">
        <form className="panel document-form" onSubmit={submit}>
          <div className="panel-head">
            <div>
              <h2>Ingest document</h2>
              <p>Text is chunked, embedded and stored in pgvector.</p>
            </div>
          </div>
          <label>
            Title
            <input
              required
              maxLength={255}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Incident Management Guide"
            />
          </label>
          <label>
            Content
            <textarea
              required
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={12}
              placeholder="Paste enterprise documentation here..."
            />
          </label>
          <button className="primary-btn" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="spin" size={16} /> Indexing...
              </>
            ) : (
              <>
                <Upload size={16} /> Ingest & index
              </>
            )}
          </button>
          {result && (
            <div className={result.error ? "error-box" : "success-box"}>
              {result.error ||
                `Document "${result.document?.title}" ingested successfully.`}
            </div>
          )}
        </form>
        <div className="panel pipeline-card">
          <div className="panel-head">
            <div>
              <h2>Ingestion pipeline</h2>
              <p>What happens after submission</p>
            </div>
          </div>
          {[
            "Document stored",
            "Text chunks generated",
            "Ollama embedding created",
            "768D vector stored",
            "Available for RAG",
          ].map((x, i) => (
            <div className="pipeline-step" key={x}>
              <span>{i + 1}</span>
              <div>
                <strong>{x}</strong>
                <small>
                  {i === 0
                    ? "PostgreSQL"
                    : i === 1
                      ? "800 character chunks"
                      : i === 2
                        ? "nomic-embed-text"
                        : "pgvector"}
                </small>
              </div>
              <CheckCircle2 size={17} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
