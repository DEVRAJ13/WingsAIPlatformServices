import { useState } from "react";
import {
  Activity,
  BookOpen,
  Bot,
  Check,
  Copy,
  Loader2,
  Send,
  Sparkles,
  Ticket,
} from "lucide-react";

import { askAgent } from "../api/agent";
import Badge from "../components/common/Badge";

const suggestions = [
  "What should happen during a critical incident?",
  "Explain the incident management process",
  "What does the WINGS incident guide say?",
  "Diagnose incident 25",
];

export default function AIConsole() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  async function submit(event, value = question) {
    event?.preventDefault();

    const q = String(value || "").trim();

    if (!q || loading) {
      return;
    }

    setQuestion("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: q,
      },
    ]);

    try {
      const data = await askAgent(q);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          data,
        },
      ]);
    } catch (error) {
      const message =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error?.message ||
        "The AI service is currently unavailable.";

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          data: {
            answer: message,
            sources: [],
            intent: "error",
          },
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function copy(text) {
    if (!text) {
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="ai-layout">
      <section className="ai-main panel">
        {messages.length === 0 ? (
          <div className="ai-empty">
            <div className="ai-icon">
              <Bot size={30} />
            </div>

            <div className="eyebrow">
              <Sparkles size={13} />
              WINGS INTELLIGENCE
            </div>

            <h1>Ask WINGS anything</h1>

            <p>
              Search enterprise knowledge, understand incidents, and get
              operational guidance without bypassing human approval.
            </p>

            <div className="suggestion-grid">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => submit(null, suggestion)}
                  disabled={loading}
                >
                  <span>{suggestion}</span>
                  <Send size={14} />
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-scroll">
            {messages.map((message, index) => {
              if (message.role === "user") {
                return (
                  <div className="message user-message" key={index}>
                    <div className="message-avatar user-avatar">DT</div>

                    <div className="message-bubble">
                      {message.text}
                    </div>
                  </div>
                );
              }

              const data = message.data || {};

              return (
                <div
                  className="message assistant-message"
                  key={index}
                >
                  <div className="message-avatar ai-avatar">
                    <Bot size={16} />
                  </div>

                  <div className="assistant-body">
                    <div className="answer-head">
                      <Badge tone={data.intent === "error" ? "danger" : "info"}>
                        {data.intent || "knowledge"}
                      </Badge>

                      <button
                        type="button"
                        className="copy-btn"
                        onClick={() => copy(data.answer)}
                        disabled={!data.answer}
                        title="Copy answer"
                      >
                        {copied ? (
                          <Check size={14} />
                        ) : (
                          <Copy size={14} />
                        )}
                      </button>
                    </div>

                    <div className="answer-text">
                      {data.answer || "No answer returned."}
                    </div>

                    {data.workflow_id && (
                      <div className="workflow-chip">
                        <span>Workflow</span>
                        <strong>{data.workflow_id}</strong>
                        {data.approval_id && (
                          <span>Approval #{data.approval_id} · waiting for human approval</span>
                        )}
                      </div>
                    )}

                    {data.diagnosis && (
                      <div className="source-card">
                        <div>
                          <strong>Incident diagnosis</strong>

                          <span>
                            Incident #
                            {data.diagnosis.id ?? "-"} ·{" "}
                            {data.diagnosis.status || "unknown status"}
                          </span>
                        </div>

                        <Badge tone="info">DIAGNOSIS</Badge>
                      </div>
                    )}

                    {Array.isArray(data.sources) &&
                      data.sources.length > 0 && (
                        <div className="sources">
                          <div className="source-title">
                            <BookOpen size={14} />
                            Sources
                          </div>

                          {data.sources.map((source, sourceIndex) => (
                            <div
                              className="source-card"
                              key={`${source.document_id ?? "document"}-${
                                source.chunk_id ?? sourceIndex
                              }-${sourceIndex}`}
                            >
                              <div>
                                <strong>
                                  {source.document_title ||
                                    `Document ${
                                      source.document_id ?? "-"
                                    }`}
                                </strong>

                                <span>
                                  Chunk {source.chunk_id ?? "-"} · Similarity{" "}
                                  {typeof source.similarity === "number"
                                    ? `${(
                                        source.similarity * 100
                                      ).toFixed(1)}%`
                                    : "-"}
                                </span>
                              </div>

                              <Badge tone="success">GROUNDED</Badge>
                            </div>
                          ))}
                        </div>
                      )}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="message assistant-message">
                <div className="message-avatar ai-avatar">
                  <Bot size={16} />
                </div>

                <div className="typing">
                  <Loader2 size={16} className="spin" />
                  WINGS is thinking...
                </div>
              </div>
            )}
          </div>
        )}

        <form className="chat-input-wrap" onSubmit={submit}>
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about incidents, procedures, knowledge, or operations..."
            disabled={loading}
          />

          <button
            type="submit"
            disabled={!question.trim() || loading}
            title="Send"
          >
            {loading ? (
              <Loader2 size={18} className="spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </form>
      </section>

      <aside className="ai-side">
        <div className="panel side-card">
          <h3>AI capabilities</h3>

          <div className="capability">
            <BookOpen size={17} />

            <div>
              <strong>Knowledge</strong>
              <span>RAG with pgvector sources</span>
            </div>
          </div>

          <div className="capability">
            <Activity size={17} />

            <div>
              <strong>Incident diagnosis</strong>
              <span>AI-assisted investigation</span>
            </div>
          </div>

          <div className="capability">
            <Ticket size={17} />

            <div>
              <strong>ITSM actions</strong>
              <span>Human approval required</span>
            </div>
          </div>
        </div>

        <div className="panel side-card">
          <h3>Safety model</h3>

          <p className="side-note">
            WINGS can recommend operational actions, but tool execution is
            protected by an explicit human approval workflow.
          </p>

          <div className="safety-line">
            <span className="status-dot" />
            Approval gate active
          </div>
        </div>
      </aside>
    </div>
  );
}