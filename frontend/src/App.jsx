
import { useEffect, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API = "http://127.0.0.1:5000";

const emptyDashboard = {
  total_analyses: 0,
  low_risk: 0,
  medium_risk: 0,
  high_risk: 0,
  blocked_responses: 0,
  average_risk_score: 0,
};

function riskName(value) {
  const risk = String(value || "low").toLowerCase();
  if (risk.includes("high")) return "High";
  if (risk.includes("medium") || risk.includes("moderate")) return "Medium";
  return "Low";
}

function pretty(value) {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function Badge({ value, type = "" }) {
  return (
    <span className={`badge ${type}`}>
      {String(value || "Not available").replaceAll("_", " ").toUpperCase()}
    </span>
  );
}

function Metric({ label, value, note }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value ?? 0}</strong>
      {note && <small>{note}</small>}
    </div>
  );
}

function SectionTitle({ number, title, subtitle }) {
  return (
    <div className="section-title">
      <span className="step-number">{number}</span>
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
    </div>
  );
}

function DateText({ value }) {
  if (!value) return <>Date unavailable</>;
  const date = new Date(value);
  return <>{Number.isNaN(date.getTime()) ? value : date.toLocaleString()}</>;
}

export default function App() {
  const [page, setPage] = useState("chat");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [dashboard, setDashboard] = useState(emptyDashboard);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [error, setError] = useState("");
  const [connectionError, setConnectionError] = useState("");

  async function loadDashboard() {
    const response = await axios.get(`${API}/api/dashboard`);
    setDashboard({
      ...emptyDashboard,
      ...(response.data?.dashboard || response.data || {}),
    });
  }

  async function loadHistory() {
    const response = await axios.get(`${API}/api/history?limit=100`);
    const rows =
      response.data?.history ??
      response.data?.data?.history ??
      [];
    setHistory(Array.isArray(rows) ? rows : []);
  }

  async function refreshData() {
    setRefreshing(true);
    try {
      await Promise.all([loadDashboard(), loadHistory()]);
      setConnectionError("");
    } catch {
      setConnectionError(
        "Cannot reach the backend. Check that Flask is running at 127.0.0.1:5000."
      );
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    refreshData();
  }, []);

  async function analyseQuestion(event) {
    event.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await axios.post(
        `${API}/api/analyze`,
        { question: question.trim() },
        { headers: { "Content-Type": "application/json" } }
      );

      const data = response.data;
      if (data?.success === false) {
        throw new Error(data.message || data.error || "Analysis failed.");
      }

      setResult(data);
      setQuestion("");
      setConnectionError("");
      await Promise.all([loadDashboard(), loadHistory()]);
    } catch (err) {
      setError(
        err.response?.data?.message ||
          err.response?.data?.error ||
          err.message ||
          "Could not analyse this question."
      );
    } finally {
      setLoading(false);
    }
  }

  async function clearHistory() {
    if (!history.length || clearing) return;
    if (!window.confirm("Delete all saved analysis history?")) return;

    setClearing(true);
    setError("");

    try {
      await axios.delete(`${API}/api/history`);
      setHistory([]);
      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.message || "Unable to clear history."
      );
    } finally {
      setClearing(false);
    }
  }

  function openHistoryItem(item) {
    setResult({
      question: item.question,
      safe_response: item.safe_response,
      risk_level: item.risk_level,
      risk_score: item.risk_score,
      delivery_action: item.delivery_action,
      response_blocked: item.response_blocked,
      flag_count: item.flag_count,
      safety_explanations: item.safety_explanations || [],
      verification_status: item.verification_status,
      verification_score: item.verification_score,
      verified_claim_count: item.verified_claim_count,
      supported_claim_count: item.supported_claim_count,
      uncertain_claim_count: item.uncertain_claim_count,
      unsupported_claim_count: item.unsupported_claim_count,
      flags: item.flags || [],
    });
    setPage("chat");
    setError("");
  }

  const risk = riskName(result?.risk_level);
  const flags = Array.isArray(result?.flags) ? result.flags : [];
  const explanations = Array.isArray(result?.safety_explanations)
    ? result.safety_explanations
    : [];

  const generatedText =
    result?.ai_response ||
    result?.generated_response ||
    result?.safe_response ||
    "No response was returned by the backend.";

  const guardedText = result?.safe_response;
  const verificationScore = result?.verification_score;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">M</div>
          <div>
            <strong>MedGuard <span>AI</span></strong>
            <small>SAFETY MIDDLEWARE</small>
          </div>
        </div>

        <p className="nav-label">MENU</p>

        <nav>
          <button
            className={page === "chat" ? "nav-link active" : "nav-link"}
            onClick={() => setPage("chat")}
          >
            <span>◉</span> Chatbot
          </button>

          <button
            className={page === "dashboard" ? "nav-link active" : "nav-link"}
            onClick={() => setPage("dashboard")}
          >
            <span>▦</span> Dashboard
          </button>

          <button
            className={page === "history" ? "nav-link active" : "nav-link"}
            onClick={() => {
              setPage("history");
              loadHistory().catch(() =>
                setConnectionError("Unable to load saved history.")
              );
            }}
          >
            <span>◷</span> History
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-indicator">
            <span className={connectionError ? "dot offline" : "dot"} />
            <div>
              <strong>{connectionError ? "Connection issue" : "Safety system"}</strong>
              <small>{connectionError ? "Check backend" : "Middleware ready"}</small>
            </div>
          </div>
          <p>Final-year academic project</p>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <span className="muted">MedGuard AI</span>
            <span className="slash"> / </span>
            <strong>
              {page === "chat"
                ? "Chatbot"
                : page === "dashboard"
                  ? "Dashboard"
                  : "History"}
            </strong>
          </div>
          <button className="refresh-button" onClick={refreshData} disabled={refreshing}>
            {refreshing ? "Refreshing…" : "↻ Refresh"}
          </button>
        </header>

        <div className="content">
          {connectionError && (
            <div className="notice warning">{connectionError}</div>
          )}
          {error && (
            <div className="notice error">
              <span>{error}</span>
              <button onClick={() => setError("")}>×</button>
            </div>
          )}

          {/* CHATBOT: RESPONSE, HALLUCINATION CHECK AND RISK ON ONE PAGE */}
          {page === "chat" && (
            <section>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">AI RESPONSE PROTECTION</span>
                  <h1>Diabetes Health Chatbot</h1>
                  <p>
                    Ask a question and review the generated response,
                    hallucination checks and risk classification below.
                  </p>
                </div>
                <span className="system-pill"><span className="dot" /> Safety checks</span>
              </div>

              <section className="chat-card">
                <div className="chat-header">
                  <div className="bot-avatar">M</div>
                  <div>
                    <strong>MedGuard Assistant</strong>
                    <small>Diabetes information · Safety analysis</small>
                  </div>
                  <span className="online-label">● READY</span>
                </div>

                <form className="question-form" onSubmit={analyseQuestion}>
                  <label htmlFor="question">Ask your question</label>
                  <textarea
                    id="question"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        analyseQuestion(event);
                      }
                    }}
                    placeholder="Example: What are common symptoms of diabetes?"
                    rows={3}
                    disabled={loading}
                  />
                  <div className="form-bottom">
                    <span>Enter to submit · Shift + Enter for a new line</span>
                    <button type="submit" disabled={loading || !question.trim()}>
                      {loading ? "Analysing…" : "Generate & Analyse →"}
                    </button>
                  </div>
                </form>

                {loading && (
                  <div className="loading-panel">
                    <div className="spinner" />
                    <div>
                      <strong>Analysing your question</strong>
                      <p>Generating a response and running safety checks…</p>
                    </div>
                  </div>
                )}

                {!result && !loading && (
                  <div className="welcome-panel">
                    <div className="welcome-icon">✦</div>
                    <h3>Your analysis will appear here</h3>
                    <p>
                      Submit a question to see the response, hallucination
                      detection results and risk classification in one place.
                    </p>
                  </div>
                )}

                {result && !loading && (
                  <div className="analysis-results">
                    <div className="result-heading">
                      <div>
                        <span className="eyebrow">ANALYSIS RESULT</span>
                        <h2>Response & Safety Report</h2>
                      </div>
                      <button className="text-button" onClick={() => setResult(null)}>
                        New analysis
                      </button>
                    </div>

                    <div className="question-summary">
                      <span className="summary-label">YOUR QUESTION</span>
                      <p>{result.question || "Question unavailable"}</p>
                    </div>

                    <section className="result-section">
                      <SectionTitle
                        number="01"
                        title="Generated Response"
                        subtitle="The model output returned by your backend"
                      />
                      <div className="response-box">
                        <div className="response-box-label">
                          <span>AI RESPONSE</span>
                          <Badge value="Unverified" type="badge-warning" />
                        </div>
                        <div className="response-text">
                          <ReactMarkdown>{generatedText}</ReactMarkdown>
                        </div>
                        <p className="unverified-note">
                          This response is shown for project evaluation. It has
                          not been established as medically accurate; do not use
                          it to make treatment decisions.
                        </p>
                      </div>
                    </section>

                    <section className="result-section">
                      <SectionTitle
                        number="02"
                        title="Hallucination Detection"
                        subtitle="Review the claim-checking results returned by the backend"
                      />

                      <div className="verification-banner">
                        <div>
                          <span className="summary-label">VERIFICATION STATUS</span>
                          <strong>
                            {pretty(result.verification_status || "Not reported")}
                          </strong>
                        </div>
                        <div>
                          <span className="summary-label">VERIFICATION SCORE</span>
                          <strong>
                            {verificationScore === undefined ||
                            verificationScore === null
                              ? "N/A"
                              : `${verificationScore}${Number(verificationScore) <= 1 ? "" : ""}`}
                          </strong>
                        </div>
                      </div>

                      <div className="claim-grid">
                        <Metric label="Verified claims" value={result.verified_claim_count} />
                        <Metric label="Supported claims" value={result.supported_claim_count} />
                        <Metric label="Uncertain claims" value={result.uncertain_claim_count} />
                        <Metric label="Unsupported claims" value={result.unsupported_claim_count} />
                      </div>

                      {flags.length > 0 && (
                        <div className="flags-panel">
                          <h3>Detected flags ({flags.length})</h3>
                          <ul>
                            {flags.map((flag, index) => (
                              <li key={index}>
                                {typeof flag === "string"
                                  ? flag
                                  : flag.message ||
                                    flag.description ||
                                    flag.type ||
                                    pretty(flag)}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {result.claim_verification && (
                        <details className="technical-details">
                          <summary>View claim verification details</summary>
                          <pre>{pretty(result.claim_verification)}</pre>
                        </details>
                      )}

                      {flags.length === 0 && !result.claim_verification && (
                        <p className="subtle-note">
                          No detailed claim records were returned for this analysis.
                          This does not by itself prove the response is factual.
                        </p>
                      )}
                    </section>

                    <section className="result-section">
                      <SectionTitle
                        number="03"
                        title="Risk Classification"
                        subtitle="Risk score and safety action returned by the middleware"
                      />

                      <div className={`risk-summary risk-${risk.toLowerCase()}`}>
                        <div>
                          <span className="summary-label">CLASSIFIED RISK</span>
                          <strong>{risk.toUpperCase()} RISK</strong>
                          <p>{result.risk_message || "Classification produced by the safety middleware."}</p>
                        </div>
                        <div className="risk-score">
                          <strong>{result.risk_score ?? "N/A"}</strong>
                          <span>Risk score</span>
                        </div>
                      </div>

                      <div className="classification-grid">
                        <div className="classification-item">
                          <span>Delivery action</span>
                          <Badge
                            value={result.delivery_action || "Not reported"}
                            type={
                              String(result.delivery_action || "").toLowerCase().includes("block")
                                ? "badge-danger"
                                : String(result.delivery_action || "").toLowerCase().includes("review")
                                  ? "badge-warning"
                                  : "badge-success"
                            }
                          />
                        </div>
                        <div className="classification-item">
                          <span>Response blocked</span>
                          <strong>{result.response_blocked ? "Yes" : "No"}</strong>
                        </div>
                        <div className="classification-item">
                          <span>Safety flags</span>
                          <strong>{result.flag_count ?? flags.length}</strong>
                        </div>
                        <div className="classification-item">
                          <span>Scoring method</span>
                          <strong>{result.scoring_method || "N/A"}</strong>
                        </div>
                      </div>

                      {explanations.length > 0 && (
                        <div className="flags-panel">
                          <h3>Safety explanations</h3>
                          <ul>
                            {explanations.map((item, index) => (
                              <li key={index}>
                                {typeof item === "string"
                                  ? item
                                  : item.message ||
                                    item.description ||
                                    pretty(item)}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {guardedText && (
                        <div className="guarded-response">
                          <div className="guarded-title">
                            <span>✓</span>
                            <div>
                              <strong>Guarded Response</strong>
                              <small>Response supplied by the safety middleware</small>
                            </div>
                          </div>
                          <div className="response-text">
                            <ReactMarkdown>{guardedText}</ReactMarkdown>
                          </div>
                        </div>
                      )}
                    </section>

                    <p className="disclaimer">
                      Academic prototype only. Hallucination indicators and risk
                      scores are not clinical validation or medical advice.
                    </p>
                  </div>
                )}
              </section>
            </section>
          )}

          {/* DASHBOARD */}
          {page === "dashboard" && (
            <section>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">SYSTEM OVERVIEW</span>
                  <h1>Dashboard</h1>
                  <p>Overview of recorded response analyses and risk outcomes.</p>
                </div>
              </div>

              <div className="metric-grid">
                <Metric label="Total analyses" value={dashboard.total_analyses} />
                <Metric label="Low risk" value={dashboard.low_risk} />
                <Metric label="Medium risk" value={dashboard.medium_risk} />
                <Metric label="High risk" value={dashboard.high_risk} />
                <Metric label="Blocked responses" value={dashboard.blocked_responses} />
                <Metric label="Average risk score" value={Number(dashboard.average_risk_score || 0).toFixed(1)} />
              </div>

              <section className="panel dashboard-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Risk distribution</h2>
                    <p>Based on saved analyses</p>
                  </div>
                </div>

                {Number(dashboard.total_analyses) === 0 ? (
                  <p className="empty-message">No analysis data yet. Start by asking a question in the Chatbot.</p>
                ) : (
                  <div className="distribution">
                    {[
                      ["Low risk", dashboard.low_risk, "low"],
                      ["Medium risk", dashboard.medium_risk, "medium"],
                      ["High risk", dashboard.high_risk, "high"],
                    ].map(([label, value, type]) => {
                      const percentage = Number(dashboard.total_analyses)
                        ? (Number(value || 0) / Number(dashboard.total_analyses)) * 100
                        : 0;
                      return (
                        <div className="distribution-row" key={type}>
                          <div><span>{label}</span><strong>{value || 0}</strong></div>
                          <div className="track">
                            <div className={`fill fill-${type}`} style={{ width: `${Math.min(100, percentage)}%` }} />
                          </div>
                          <small>{percentage.toFixed(0)}%</small>
                        </div>
                      );
                    })}
                  </div>
                )}
              </section>

              <section className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Recent analyses</h2>
                    <p>Latest saved questions</p>
                  </div>
                  <button className="text-button" onClick={() => setPage("history")}>View history →</button>
                </div>
                {history.length === 0 ? (
                  <p className="empty-message">No history recorded yet.</p>
                ) : (
                  <div className="recent-list">
                    {history.slice(0, 5).map((item, index) => (
                      <button className="recent-row" key={item.id ?? index} onClick={() => openHistoryItem(item)}>
                        <span className="recent-question">{item.question}</span>
                        <Badge value={`${riskName(item.risk_level)} risk`} type={`risk-badge-${riskName(item.risk_level).toLowerCase()}`} />
                        <span className="recent-date"><DateText value={item.created_at} /></span>
                      </button>
                    ))}
                  </div>
                )}
              </section>
            </section>
          )}

          {/* HISTORY */}
          {page === "history" && (
            <section>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">SAVED ANALYSES</span>
                  <h1>History</h1>
                  <p>Previous questions and their recorded safety classifications.</p>
                </div>
                <button className="danger-button" disabled={!history.length || clearing} onClick={clearHistory}>
                  {clearing ? "Clearing…" : "Clear history"}
                </button>
              </div>

              <div className="history-count">
                <strong>{history.length}</strong>
                <span>saved analyses</span>
              </div>

              <section className="panel history-panel">
                {history.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-symbol">◷</div>
                    <h2>No history yet</h2>
                    <p>Ask a question in the Chatbot to save your first analysis.</p>
                    <button onClick={() => setPage("chat")}>Open chatbot</button>
                  </div>
                ) : (
                  history.map((item, index) => (
                    <article className="history-row" key={item.id ?? index}>
                      <div className="history-row-top">
                        <div className="history-question">
                          <strong>{item.question || "Untitled question"}</strong>
                          <small><DateText value={item.created_at} /></small>
                        </div>
                        <Badge value={`${riskName(item.risk_level)} risk`} type={`risk-badge-${riskName(item.risk_level).toLowerCase()}`} />
                      </div>

                      <div className="history-meta">
                        <span>Risk score: <strong>{item.risk_score ?? "N/A"}</strong></span>
                        <span>Flags: <strong>{item.flag_count ?? 0}</strong></span>
                        <span>Action: <strong>{item.delivery_action || "N/A"}</strong></span>
                        <button className="text-button" onClick={() => openHistoryItem(item)}>
                          View analysis →
                        </button>
                      </div>

                      {item.safe_response && (
                        <details className="history-response">
                          <summary>View saved guarded response</summary>
                          <div className="response-text">
                            <ReactMarkdown>{item.safe_response}</ReactMarkdown>
                          </div>
                        </details>
                      )}
                    </article>
                  ))
                )}
              </section>
            </section>
          )}

          <footer className="footer">
            MedGuard AI · Diabetes response safety middleware · Academic prototype
          </footer>
        </div>
      </main>
    </div>
  );
}
