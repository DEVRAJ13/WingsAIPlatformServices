import { useState } from "react";
import {
  BookOpen,
  Search,
  Sparkles,
  FileText,
  Loader2,
} from "lucide-react";
import { Link } from "react-router-dom";

import Badge from "../components/common/Badge";
import { queryKnowledge } from "../api/documents";

export default function Knowledge() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function search(event) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await queryKnowledge(trimmedQuestion);
      setResult(response);
    } catch (err) {
      setResult(null);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Knowledge search failed.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <div className="page-intro">
        <div>
          <div className="eyebrow">
            <BookOpen size={13} />
            RAG KNOWLEDGE
          </div>

          <h1>Enterprise knowledge</h1>

          <p>
            Search indexed operational documentation using semantic retrieval.
          </p>
        </div>

        <Link to="/documents" className="primary-btn">
          <FileText size={16} />
          Manage documents
        </Link>
      </div>

      <form className="knowledge-search panel" onSubmit={search}>
        <Search size={20} />

        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Search knowledge, procedures, incident guides..."
          disabled={loading}
        />

        <button
          type="submit"
          className="primary-btn"
          disabled={loading || !question.trim()}
        >
          {loading ? (
            <Loader2 className="spin" size={16} />
          ) : (
            <Sparkles size={16} />
          )}

          Search
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Answer</h2>
              <p>{result.model || "WINGS RAG"}</p>
            </div>
          </div>

          <div className="description-box">
            <p>{result.answer}</p>
          </div>

          {result.sources?.length > 0 && (
            <div className="sources">
              {result.sources.map((source, index) => (
                <div
                  className="source-card"
                  key={`${source.document_id}-${source.chunk_id}-${index}`}
                >
                  <div>
                    <strong>
                      {source.document_title ||
                        `Document ${source.document_id}`}
                    </strong>

                    <span>
                      Chunk {source.chunk_id ?? "-"} ·{" "}
                      {typeof source.distance === "number"
                        ? `Distance ${source.distance.toFixed(4)}`
                        : typeof source.similarity === "number"
                          ? `Similarity ${source.similarity.toFixed(4)}`
                          : "Retrieved"}
                    </span>
                  </div>

                  <Badge tone="success">GROUNDED</Badge>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}