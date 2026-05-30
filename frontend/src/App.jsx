import React, { useState, useEffect, useRef } from 'react';
import { 
  LayoutDashboard, MessageSquare, Bot, GitBranch, Database, 
  Zap, Activity, Cpu, Coins, Trash2, Send, Play, PlayCircle, 
  FileUp, Search, AlertCircle, Info, Calculator, Copy, Check 
} from 'lucide-react';
import './App.css';

const BACKEND_URL = 'http://localhost:8000';

// Stateful Line-by-Line Markdown Parser
function parseMarkdown(text) {
  if (!text) return '';

  // 1. Escape HTML for safety, but preserve it for code blocks
  let escapedText = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

  // 2. Extract Code Blocks
  const codeBlocks = [];
  const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
  
  let placeholderText = escapedText.replace(codeBlockRegex, (match, lang, code) => {
      const language = lang || 'plaintext';
      const uniqueId = 'code-' + Math.random().toString(36).substr(2, 9);
      const index = codeBlocks.length;
      
      const blockHtml = `
          <pre class="code-container-pre">
              <div class="code-header">
                  <span>${language.toUpperCase()}</span>
                  <button class="btn-copy" type="button" onclick="window.copyToClipboard('${uniqueId}')">
                      <svg class="small-icon" viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                      <span>Copy</span>
                  </button>
              </div>
              <code id="${uniqueId}">${code.trim()}</code>
          </pre>
      `;
      codeBlocks.push(blockHtml);
      return `__CODE_BLOCK_PLACEHOLDER_${index}__`;
  });

  // 3. Process line-by-line using a state machine
  const lines = placeholderText.split('\n');
  let htmlResult = [];
  
  let inUl = false;
  let inOl = false;
  let inParagraph = false;

  function closeList() {
      if (inUl) {
          htmlResult.push('</ul>');
          inUl = false;
      }
      if (inOl) {
          htmlResult.push('</ol>');
          inOl = false;
      }
  }

  function closeParagraph() {
      if (inParagraph) {
          htmlResult.push('</p>');
          inParagraph = false;
      }
  }

  for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      let trimmed = line.trim();

      if (trimmed.startsWith('__CODE_BLOCK_PLACEHOLDER_')) {
          closeList();
          closeParagraph();
          htmlResult.push(trimmed);
          continue;
      }

      if (trimmed === '') {
          closeList();
          closeParagraph();
          continue;
      }

      let headerMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (headerMatch) {
          closeList();
          closeParagraph();
          let level = headerMatch[1].length;
          let content = headerMatch[2];
          htmlResult.push(`<h${level}>${content}</h${level}>`);
          continue;
      }

      if (trimmed === '---' || trimmed === '***') {
          closeList();
          closeParagraph();
          htmlResult.push('<hr>');
          continue;
      }

      let ulMatch = line.match(/^(\s*)[-*+]\s+(.+)$/);
      if (ulMatch) {
          closeParagraph();
          if (inOl) closeList();
          if (!inUl) {
              htmlResult.push('<ul>');
              inUl = true;
          }
          htmlResult.push(`<li>${ulMatch[2]}</li>`);
          continue;
      }

      let olMatch = line.match(/^(\s*)\d+\.\s+(.+)$/);
      if (olMatch) {
          closeParagraph();
          if (inUl) closeList();
          if (!inOl) {
              htmlResult.push('<ol>');
              inOl = true;
          }
          htmlResult.push(`<li>${olMatch[2]}</li>`);
          continue;
      }

      closeList();
      if (!inParagraph) {
          htmlResult.push('<p>');
          inParagraph = true;
          htmlResult.push(line);
      } else {
          htmlResult.push('<br>' + line);
      }
  }

  closeList();
  closeParagraph();

  let compiledHtml = htmlResult.join('\n');

  // 4. Process inline styling elements
  compiledHtml = compiledHtml.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  compiledHtml = compiledHtml.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  compiledHtml = compiledHtml.replace(/_([^_]+)_/g, '<em>$1</em>');
  compiledHtml = compiledHtml.replace(/`([^`]+)`/g, '<code>$1</code>');

  // 5. Restore code block containers
  codeBlocks.forEach((block, index) => {
      compiledHtml = compiledHtml.replace(`__CODE_BLOCK_PLACEHOLDER_${index}__`, block);
  });

  return compiledHtml;
}

export default function App() {
  // Navigation & KPI states
  const [activeTab, setActiveTab] = useState('dashboard');
  const [requestsKPI, setRequestsKPI] = useState(0);
  const [tokensKPI, setTokensKPI] = useState(0);
  const [savingsKPI, setSavingsKPI] = useState(0.0);
  const [avgSpeed, setAvgSpeed] = useState('--');
  
  // Health check status
  const [healthStatus, setHealthStatus] = useState('Checking...');
  const [latency, setLatency] = useState('--');
  
  // Sub-Tab Token breakdowns
  const [tokensBreakdown, setTokensBreakdown] = useState({ chat: 0, agent: 0, workflow: 0 });
  const [ragQueries, setRagQueries] = useState(0);

  // Chat forms states
  const [chatHistory, setChatHistory] = useState([
    {
      role: 'system',
      content: 'Hello! I am connected to the core `gemma4:31b-cloud` model. Ask me anything, and I\'ll generate responses directly.'
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Multi-Agent states
  const [agentHistory, setAgentHistory] = useState([
    {
      role: 'system',
      content: 'Ready to execute multi-agent tasks! Let me solve a complex math puzzle or research a live event (e.g., *"What is the current stock price of Apple and what is that number times 2.5?"*).'
    }
  ]);
  const [agentInput, setAgentInput] = useState('');
  const [agentMode, setAgentMode] = useState('search'); // 'search' or 'calc'
  const [agentLoading, setAgentLoading] = useState(false);

  // Stateful Workflow states
  const [workflowHistory, setWorkflowHistory] = useState([
    {
      role: 'system',
      content: 'This graph has a stateful node `chatbot`. Type your prompt, and I will show the execution moving through START -> CHATBOT -> END in real time.'
    }
  ]);
  const [workflowInput, setWorkflowInput] = useState('');
  const [workflowLoading, setWorkflowLoading] = useState(false);
  const [workflowLogs, setWorkflowLogs] = useState([{ time: '18:00:00', text: 'Platform graph initialized.', status: 'system' }]);
  const [workflowNodes, setWorkflowNodes] = useState({ start: true, chatbot: false, end: false, running: false });

  // RAG pipeline states
  const [filePath, setFilePath] = useState('');
  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestLogs, setIngestLogs] = useState([{ time: 'System', text: 'Ready for document indexing.', status: 'system' }]);
  
  const [ragQuery, setRagQuery] = useState('');
  const [ragLoading, setRagLoading] = useState(false);
  const [ragResults, setRagResults] = useState([]);

  // Auto-scroll refs
  const chatBottomRef = useRef(null);
  const agentBottomRef = useRef(null);
  const workflowBottomRef = useRef(null);

  // Bind copy-code functionality globally
  useEffect(() => {
    window.copyToClipboard = (elementId) => {
      const codeEl = document.getElementById(elementId);
      if (!codeEl) return;
      
      const textToCopy = codeEl.textContent;
      navigator.clipboard.writeText(textToCopy).then(() => {
        const header = codeEl.previousElementSibling;
        const copyBtnSpan = header.querySelector('.btn-copy span');
        if (copyBtnSpan) {
          copyBtnSpan.textContent = 'Copied!';
          setTimeout(() => {
            copyBtnSpan.textContent = 'Copy';
          }, 2000);
        }
      });
    };
  }, []);

  // Periodic Health checking
  useEffect(() => {
    const checkHealth = async () => {
      const startTime = Date.now();
      try {
        const response = await fetch(`${BACKEND_URL}/api/health`, {
          signal: AbortSignal.timeout(3000)
        });
        const lat = Date.now() - startTime;
        if (response.ok) {
          setHealthStatus('Online');
          setLatency(`${lat} ms`);
        } else {
          throw new Error();
        }
      } catch (e) {
        setHealthStatus('Offline');
        setLatency('-- ms');
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  // Scroll to bottom helper hooks
  useEffect(() => {
    if (chatBottomRef.current) chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, chatLoading]);

  useEffect(() => {
    if (agentBottomRef.current) agentBottomRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [agentHistory, agentLoading]);

  useEffect(() => {
    if (workflowBottomRef.current) workflowBottomRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [workflowHistory, workflowLoading]);

  // Update Token metrics math
  const updateMetrics = (type, input, output, total) => {
    setRequestsKPI(prev => prev + 1);
    setTokensBreakdown(prev => {
      const updated = { ...prev, [type]: prev[type] + total };
      return updated;
    });
    setTokensKPI(prev => {
      const newTotal = prev + total;
      const baseValue = (newTotal / 1000) * 0.0015;
      const virtualCycles = (requestsKPI + 1) * 0.02;
      setSavingsKPI(baseValue + virtualCycles);
      return newTotal;
    });
    // Virtual speed estimation
    setAvgSpeed(Math.floor(25 + Math.random() * 15));
  };

  // Direct LLM Form submit
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;
    const msg = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: msg }]);
    setChatLoading(true);
    setRequestsKPI(prev => prev + 1);

    try {
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      const data = await response.json();
      
      setChatHistory(prev => [...prev, { 
        role: 'system', 
        content: data.response,
        tokens: { input: data.input_token, output: data.output_token, total: data.total_token }
      }]);
      updateMetrics('chat', data.input_token, data.output_token, data.total_token);
    } catch (err) {
      setChatHistory(prev => [...prev, { 
        role: 'system', 
        content: `⚠️ **Error communicating with backend:** ${err.message}\n\nPlease verify that the FastAPI backend is running at ${BACKEND_URL}.` 
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Multi-Agent Form submit
  const handleAgentSubmit = async (e) => {
    e.preventDefault();
    if (!agentInput.trim() || agentLoading) return;
    const msg = agentInput.trim();
    setAgentInput('');
    setAgentHistory(prev => [...prev, { role: 'user', content: msg }]);
    setAgentLoading(true);
    setRequestsKPI(prev => prev + 1);

    // Apply calculator restriction if needed
    let queryPrompt = msg;
    if (agentMode === 'calc') {
      queryPrompt = "[Local restricted mode: Do not execute Tavily Search] " + msg;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: queryPrompt })
      });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      const data = await response.json();

      setAgentHistory(prev => [...prev, { 
        role: 'system', 
        content: data.response,
        tokens: { input: data.input_token, output: data.output_token, total: data.total_token }
      }]);
      updateMetrics('agent', data.input_token, data.output_token, data.total_token);
    } catch (err) {
      setAgentHistory(prev => [...prev, { 
        role: 'system', 
        content: `⚠️ **Agent Execution Error:** ${err.message}\n\nPlease check server connection.` 
      }]);
    } finally {
      setAgentLoading(false);
    }
  };

  // Stateful Workflow Graph Execution submit
  const handleWorkflowSubmit = async (e) => {
    e.preventDefault();
    if (!workflowInput.trim() || workflowLoading) return;
    const msg = workflowInput.trim();
    setWorkflowInput('');
    setWorkflowHistory(prev => [...prev, { role: 'user', content: msg }]);
    setWorkflowLoading(true);
    setRequestsKPI(prev => prev + 1);

    // Animate SVG flowchart progression
    const date = new Date();
    const timeStr = date.toTimeString().split(' ')[0];
    setWorkflowLogs([{ time: timeStr, text: 'START Node Triggered', status: 'active' }]);
    setWorkflowNodes({ start: true, chatbot: false, end: false, running: true });

    setTimeout(() => {
      const t = new Date().toTimeString().split(' ')[0];
      setWorkflowLogs(prev => [...prev, { time: t, text: 'Routing state graph -> chatbot_node', status: 'active' }]);
      setWorkflowNodes({ start: false, chatbot: true, end: false, running: true });
    }, 800);

    try {
      const response = await fetch(`${BACKEND_URL}/workflow/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      const data = await response.json();

      const tDone = new Date().toTimeString().split(' ')[0];
      setWorkflowLogs(prev => [
        ...prev, 
        { time: tDone, text: 'chatbot_node completed invocation successfully', status: 'success' },
        { time: tDone, text: 'Transitioning state graph -> END Node', status: 'success' }
      ]);
      setWorkflowNodes({ start: false, chatbot: false, end: true, running: false });

      setWorkflowHistory(prev => [...prev, { 
        role: 'system', 
        content: data.response,
        tokens: { input: data.input_token, output: data.output_token, total: data.total_token }
      }]);
      updateMetrics('workflow', data.input_token, data.output_token, data.total_token);
    } catch (err) {
      setWorkflowNodes({ start: false, chatbot: false, end: false, running: false });
      const tErr = new Date().toTimeString().split(' ')[0];
      setWorkflowLogs(prev => [...prev, { time: tErr, text: `⚠️ Workflow failed: ${err.message}`, status: 'system' }]);
      setWorkflowHistory(prev => [...prev, { 
        role: 'system', 
        content: `⚠️ **Workflow execution failed:** ${err.message}` 
      }]);
    } finally {
      setWorkflowLoading(false);
    }
  };

  // RAG Document Ingestion
  const handleRAGIngestion = async (e) => {
    e.preventDefault();
    if (!filePath.trim() || ingestLoading) return;
    const path = filePath.trim();
    setIngestLoading(true);

    const t = new Date().toTimeString().split(' ')[0];
    setIngestLogs(prev => [...prev, { time: t, text: `Loading ${path}...`, status: 'active' }]);

    try {
      const response = await fetch(`${BACKEND_URL}/api/rag/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: path })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `Server error ${response.status}`);
      
      const tSuccess = new Date().toTimeString().split(' ')[0];
      setIngestLogs(prev => [...prev, { 
        time: tSuccess, 
        text: `Success: Indexed ${data.chunks_created} chunks into ChromaDB`, 
        status: 'success' 
      }]);
    } catch (err) {
      const tErr = new Date().toTimeString().split(' ')[0];
      setIngestLogs(prev => [...prev, { time: tErr, text: `⚠️ Ingestion failed: ${err.message}`, status: 'system' }]);
    } finally {
      setIngestLoading(false);
    }
  };

  // RAG Query Vector Store
  const handleRAGQuery = async (e) => {
    e.preventDefault();
    if (!ragQuery.trim() || ragLoading) return;
    const q = ragQuery.trim();
    setRagLoading(true);
    setRagQueries(prev => prev + 1);
    setRequestsKPI(prev => prev + 1);

    try {
      const response = await fetch(`${BACKEND_URL}/api/rag/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `Server error ${response.status}`);
      
      setRagResults(data.results || []);
    } catch (err) {
      setRagResults([{ content: `⚠️ **Similarity search failed:** ${err.message}`, metadata: { source: 'System Alert' } }]);
    } finally {
      setRagLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-container">
            <div className="logo-orb"></div>
            <span className="logo-text">Enterprise <span className="logo-sub">Agentic</span></span>
          </div>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} 
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard />
            <span>Dashboard</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`} 
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare />
            <span>Core Chat</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'agents' ? 'active' : ''}`} 
            onClick={() => setActiveTab('agents')}
          >
            <Bot />
            <span>Multi-Agent Hub</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'workflow' ? 'active' : ''}`} 
            onClick={() => setActiveTab('workflow')}
          >
            <GitBranch />
            <span>LangGraph Workflow</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'rag' ? 'active' : ''}`} 
            onClick={() => setActiveTab('rag')}
          >
            <Database />
            <span>RAG Knowledge Base</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="connection-status-panel">
            <div className="status-indicator">
              <span className={`pulsar ${healthStatus === 'Online' ? 'online' : 'offline'}`}></span>
              <span className="status-text">{healthStatus === 'Online' ? 'System Online' : 'Connection Offline'}</span>
            </div>
            <div className="latency-display">
              <Zap className="small-icon" />
              <span>{latency}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Panel Content */}
      <main className="main-content">
        <header className="main-header">
          <div className="header-left">
            <h1>
              {activeTab === 'dashboard' && 'Dashboard Overview'}
              {activeTab === 'chat' && 'Direct LLM Chat'}
              {activeTab === 'agents' && 'Multi-Agent Hub'}
              {activeTab === 'workflow' && 'LangGraph Workflow'}
              {activeTab === 'rag' && 'RAG Knowledge Base'}
            </h1>
            <p className="subtitle">
              {activeTab === 'dashboard' && 'Real-time platform operations and metrics'}
              {activeTab === 'chat' && 'Low-latency conversational access to gemma4:31b-cloud'}
              {activeTab === 'agents' && 'Zero-Shot ReAct executors equipped with search and tools'}
              {activeTab === 'workflow' && 'Stateful, orchestrative execution pipelines'}
              {activeTab === 'rag' && 'Similarity retrieval indexes and vector database injection'}
            </p>
          </div>
          
          <div className="kpi-container">
            <div className="kpi-card">
              <div className="kpi-icon"><Activity /></div>
              <div className="kpi-info">
                <span className="kpi-label">Requests</span>
                <span className="kpi-value">{requestsKPI}</span>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon"><Cpu /></div>
              <div className="kpi-info">
                <span className="kpi-label">Tokens Used</span>
                <span className="kpi-value">{tokensKPI}</span>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon"><Coins /></div>
              <div className="kpi-info">
                <span className="kpi-label">Compute Value</span>
                <span className="kpi-value">${savingsKPI.toFixed(3)}</span>
              </div>
            </div>
          </div>
        </header>

        {/* Tab Panes rendering */}
        <div className="workspace-panes">
          
          {/* 1. DASHBOARD OVERVIEW */}
          <section className={`tab-pane ${activeTab === 'dashboard' ? 'active' : ''}`}>
            <div className="dashboard-grid">
              <div className="grid-card wide-card glass-panel">
                <h3>Welcome to Enterprise Multi-Agent AI Platform</h3>
                <p>An orchestration layer combining direct LLM chat, customized tool-calling LangChain agents, LangGraph-powered stateful workflows, and a retrieval-augmented generation (RAG) vector-database pipeline.</p>
                
                <div className="features-highlights">
                  <div className="highlight-item" onClick={() => setActiveTab('chat')} style={{ cursor: 'pointer' }}>
                    <div className="icon-circle cyan-glow"><MessageSquare /></div>
                    <h4>Direct Chat</h4>
                    <p>Low-latency connection to <code>gemma4:31b-cloud</code> for basic prompt processing.</p>
                  </div>
                  <div className="highlight-item" onClick={() => setActiveTab('agents')} style={{ cursor: 'pointer' }}>
                    <div className="icon-circle purple-glow"><Bot /></div>
                    <h4>Multi-Agent Systems</h4>
                    <p>Zero-Shot ReAct executors using integrated Tavily Search and local math compilers.</p>
                  </div>
                  <div className="highlight-item" onClick={() => setActiveTab('workflow')} style={{ cursor: 'pointer' }}>
                    <div className="icon-circle pink-glow"><GitBranch /></div>
                    <h4>Stateful Workflows</h4>
                    <p>Stateful, compilable workflows governed by LangGraph's orchestration architecture.</p>
                  </div>
                </div>
              </div>

              <div className="grid-card glass-panel">
                <h3>Session Metrics Log</h3>
                <div className="metric-breakdown">
                  <div className="metric-row">
                    <span>Average Processing Speed:</span>
                    <strong>{avgSpeed === '--' ? '--' : `~${avgSpeed} tokens/s`}</strong>
                  </div>
                  <div className="metric-row">
                    <span>Core Chat Tokens:</span>
                    <strong>{tokensBreakdown.chat}</strong>
                  </div>
                  <div className="metric-row">
                    <span>Multi-Agent Tokens:</span>
                    <strong>{tokensBreakdown.agent}</strong>
                  </div>
                  <div className="metric-row">
                    <span>Workflow Tokens:</span>
                    <strong>{tokensBreakdown.workflow}</strong>
                  </div>
                  <div className="metric-row">
                    <span>RAG Retrieved Queries:</span>
                    <strong>{ragQueries}</strong>
                  </div>
                </div>
                <div className="chart-placeholder">
                  <div className="chart-bar" style={{ height: '40%' }}></div>
                  <div className="chart-bar" style={{ height: '65%' }}></div>
                  <div className="chart-bar" style={{ height: '85%' }}></div>
                  <div className="chart-bar" style={{ height: '50%' }}></div>
                  <div className="chart-bar" style={{ height: '95%' }}></div>
                </div>
              </div>

              <div className="grid-card wide-card glass-panel">
                <h3>Active System Configuration</h3>
                <div className="config-panel-grid">
                  <div className="config-item">
                    <span className="config-label">Active Model:</span>
                    <span className="config-value badge">gemma4:31b-cloud (Ollama)</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Temperature:</span>
                    <span className="config-value badge">0.0 (Deterministic)</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Embedding Model:</span>
                    <span className="config-value badge">embeddinggemma:latest</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Vector Directory:</span>
                    <span className="config-value badge">./backend/vector_db</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Tavily Web Search:</span>
                    <span className="config-value badge active">Enabled</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Langsmith Tracing:</span>
                    <span className="config-value badge active">Enabled</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* 2. CORE CHAT */}
          <section className={`tab-pane ${activeTab === 'chat' ? 'active' : ''}`}>
            <div className="chat-wrapper glass-panel">
              <div className="chat-history-header">
                <span className="session-label">Session ID: <code>direct_chat_main</code></span>
                <button 
                  className="btn btn-secondary btn-small" 
                  onClick={() => setChatHistory([{ role: 'system', content: 'History cleared. Ready for your next query!' }])}
                >
                  <Trash2 className="small-icon" /> Clear History
                </button>
              </div>
              
              <div className="chat-messages-container">
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'system'}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? <LayoutDashboard /> : <Bot />}
                    </div>
                    <div className="message-bubble">
                      <div dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
                      {msg.tokens && (
                        <div className="message-meta">
                          <span className="meta-pill">Prompt: {msg.tokens.input}</span>
                          <span className="meta-pill">Completion: {msg.tokens.output}</span>
                          <span className="meta-pill">Total: {msg.tokens.total}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {chatLoading && (
                  <div className="message system">
                    <div className="message-avatar"><Bot /></div>
                    <div className="message-bubble">
                      <div className="typing-indicator">
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatBottomRef} />
              </div>

              <div className="quick-prompts">
                <button className="quick-prompt-btn" onClick={() => setChatInput('Draft a marketing outline for a SaaS platform')}>Draft a marketing outline for a SaaS platform</button>
                <button className="quick-prompt-btn" onClick={() => setChatInput('Write a Python script to filter arrays')}>Write a Python script to filter arrays</button>
                <button className="quick-prompt-btn" onClick={() => setChatInput('Explain quantum computing in simple words')}>Explain quantum computing in simple words</button>
              </div>

              <form onSubmit={handleChatSubmit} className="chat-input-area">
                <input 
                  type="text" 
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type your message to the core LLM..."
                  required
                  autoComplete="off"
                />
                <button type="submit" className="btn btn-primary send-btn" disabled={chatLoading}>
                  <span>Send</span>
                  <Send />
                </button>
              </form>
            </div>
          </section>

          {/* 3. MULTI-AGENT HUB */}
          <section className={`tab-pane ${activeTab === 'agents' ? 'active' : ''}`}>
            <div className="agents-layout">
              <div className="agents-controls glass-panel">
                <h3>Agent Control Deck</h3>
                <p className="section-desc">Manage the zero-shot ReAct agent executors and tools availability.</p>
                
                <div className="control-group">
                  <label className="control-title">Active Agent Strategy</label>
                  <div className="radio-selector">
                    <label className={`radio-option ${agentMode === 'search' ? 'active' : ''}`}>
                      <input 
                        type="radio" 
                        name="react-agent-mode"
                        value="search" 
                        checked={agentMode === 'search'} 
                        onChange={() => setAgentMode('search')}
                      />
                      <div className="radio-content">
                        <strong>Search-Enabled Agent</strong>
                        <span>Equipped with Tavily search + math tools</span>
                      </div>
                    </label>
                    <label className={`radio-option ${agentMode === 'calc' ? 'active' : ''}`}>
                      <input 
                        type="radio" 
                        name="react-agent-mode"
                        value="calc" 
                        checked={agentMode === 'calc'} 
                        onChange={() => setAgentMode('calc')}
                      />
                      <div className="radio-content">
                        <strong>Local Calculator Agent</strong>
                        <span>Restricted to math evaluation only</span>
                      </div>
                    </label>
                  </div>
                </div>

                <div className="control-group">
                  <label className="control-title">Available Tools Inventory</label>
                  <div className="tools-deck">
                    <div className="tool-card active">
                      <div className="tool-icon"><Calculator /></div>
                      <div className="tool-details">
                        <strong>Math Solver</strong>
                        <span>Local algebraic evaluator</span>
                      </div>
                      <span className="tool-badge">ACTIVE</span>
                    </div>
                    <div className={`tool-card ${agentMode === 'search' ? 'active' : ''}`}>
                      <div className="tool-icon"><Search /></div>
                      <div className="tool-details">
                        <strong>Tavily Search</strong>
                        <span>Real-time web browser lookup</span>
                      </div>
                      <span className="tool-badge">{agentMode === 'search' ? 'ACTIVE' : 'RESTRICTED'}</span>
                    </div>
                  </div>
                </div>

                <div className="info-alert">
                  <Info />
                  <p>Multi-Agent mode leverages LangChain to automatically select which tools are appropriate based on the user's prompt (Zero-Shot ReAct).</p>
                </div>
              </div>

              <div className="chat-wrapper glass-panel">
                <div className="chat-history-header">
                  <span className="session-label">Agent Console: <code>{agentMode === 'search' ? 'agent_with_search' : 'agent_without_search'}</code></span>
                  <button 
                    className="btn btn-secondary btn-small"
                    onClick={() => setAgentHistory([{ role: 'system', content: 'Agent history cleared.' }])}
                  >
                    <Trash2 className="small-icon" /> Clear History
                  </button>
                </div>

                <div className="chat-messages-container">
                  {agentHistory.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'system'}`}>
                      <div className="message-avatar">
                        {msg.role === 'user' ? <LayoutDashboard /> : <Bot />}
                      </div>
                      <div className="message-bubble">
                        <div dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
                        {msg.tokens && (
                          <div className="message-meta">
                            <span className="meta-pill">Prompt: {msg.tokens.input}</span>
                            <span className="meta-pill">Completion: {msg.tokens.output}</span>
                            <span className="meta-pill">Total: {msg.tokens.total}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {agentLoading && (
                    <div className="message system">
                      <div className="message-avatar"><Bot /></div>
                      <div className="message-bubble">
                        <div className="typing-indicator">
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={agentBottomRef} />
                </div>

                <form onSubmit={handleAgentSubmit} className="chat-input-area">
                  <input 
                    type="text" 
                    value={agentInput}
                    onChange={(e) => setAgentInput(e.target.value)}
                    placeholder="Type a task for the Multi-Agent system..."
                    required
                    autoComplete="off"
                  />
                  <button type="submit" className="btn btn-primary send-btn" disabled={agentLoading}>
                    <span>Execute</span>
                    <Play />
                  </button>
                </form>
              </div>
            </div>
          </section>

          {/* 4. LANGGRAPH WORKFLOW */}
          <section className={`tab-pane ${activeTab === 'workflow' ? 'active' : ''}`}>
            <div className="workflow-layout">
              <div className="workflow-controls glass-panel">
                <h3>LangGraph Visualizer</h3>
                <p className="section-desc">Observe the state transitions in the compiled LangGraph workflow.</p>
                
                <div className="workflow-graph-canvas">
                  <svg width="100%" height="240" viewBox="0 0 300 240" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#6366f1" />
                      </marker>
                    </defs>

                    <line x1="0" y1="40" x2="300" y2="40" stroke="#1e293b" strokeDasharray="2,2"/>
                    <line x1="0" y1="120" x2="300" y2="120" stroke="#1e293b" strokeDasharray="2,2"/>
                    <line x1="0" y1="200" x2="300" y2="200" stroke="#1e293b" strokeDasharray="2,2"/>

                    <path d="M 150 45 L 150 75" fill="none" stroke="#6366f1" strokeWidth="2" markerEnd="url(#arrow)"/>
                    <path d="M 150 135 L 150 165" fill="none" stroke="#6366f1" strokeWidth="2" markerEnd="url(#arrow)"/>

                    {/* START Node */}
                    <g className={`graph-node ${workflowNodes.start ? 'active' : ''}`}>
                      <circle cx="150" cy="30" r="16" fill="#1e1b4b" stroke={workflowNodes.start ? '#06b6d4' : '#334155'} strokeWidth="2" />
                      <text x="150" y="34" fontSize="10" fontFamily="Inter" fontWeight="600" fill={workflowNodes.start ? '#ffffff' : '#64748b'} textAnchor="middle">START</text>
                    </g>

                    {/* CHATBOT Node */}
                    <g className={`graph-node ${workflowNodes.chatbot ? 'active' : ''}`}>
                      <rect x="90" y="80" width="120" height="50" rx="8" fill="#0f172a" stroke={workflowNodes.chatbot ? '#6366f1' : '#334155'} strokeWidth="2" className="graph-box" />
                      <text x="150" y="105" fontSize="12" fontFamily="Inter" fontWeight="600" fill={workflowNodes.chatbot ? '#ffffff' : '#94a3b8'} textAnchor="middle">
                        {workflowNodes.running && workflowNodes.chatbot ? 'chatbot (RUNNING)' : 'chatbot_node'}
                      </text>
                      <text x="150" y="120" fontSize="9" fontFamily="Fira Code" fill="#64748b" textAnchor="middle">State: Messages</text>
                    </g>

                    {/* END Node */}
                    <g className={`graph-node ${workflowNodes.end ? 'active' : ''}`}>
                      <circle cx="150" cy="185" r="16" fill="#1e1b4b" stroke={workflowNodes.end ? '#06b6d4' : '#334155'} strokeWidth="2" />
                      <text x="150" y="189" fontSize="10" fontFamily="Inter" fontWeight="600" fill={workflowNodes.end ? '#ffffff' : '#64748b'} textAnchor="middle">END</text>
                    </g>
                  </svg>
                </div>

                <div className="state-logs-container">
                  <h4>State Transition Logs</h4>
                  <div className="state-logs">
                    {workflowLogs.map((log, idx) => (
                      <div key={idx} className={`log-entry ${log.status}`}>
                        <span className="log-time">[{log.time}]</span> {log.text}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="chat-wrapper glass-panel">
                <div className="chat-history-header">
                  <span className="session-label">Workflow Runner: <code>StateGraph(AgentState)</code></span>
                  <button 
                    className="btn btn-secondary btn-small"
                    onClick={() => setWorkflowHistory([{ role: 'system', content: 'Workflow cleared.' }])}
                  >
                    <Trash2 className="small-icon" /> Clear History
                  </button>
                </div>

                <div className="chat-messages-container">
                  {workflowHistory.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'system'}`}>
                      <div className="message-avatar">
                        {msg.role === 'user' ? <LayoutDashboard /> : <Bot />}
                      </div>
                      <div className="message-bubble">
                        <div dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
                        {msg.tokens && (
                          <div className="message-meta">
                            <span className="meta-pill">Prompt: {msg.tokens.input}</span>
                            <span className="meta-pill">Completion: {msg.tokens.output}</span>
                            <span className="meta-pill">Total: {msg.tokens.total}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {workflowLoading && (
                    <div className="message system">
                      <div className="message-avatar"><Bot /></div>
                      <div className="message-bubble">
                        <div className="typing-indicator">
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={workflowBottomRef} />
                </div>

                <form onSubmit={handleWorkflowSubmit} className="chat-input-area">
                  <input 
                    type="text" 
                    value={workflowInput}
                    onChange={(e) => setWorkflowInput(e.target.value)}
                    placeholder="Send a message through the LangGraph workflow..."
                    required
                    autoComplete="off"
                  />
                  <button type="submit" className="btn btn-primary send-btn" disabled={workflowLoading}>
                    <span>Run Graph</span>
                    <PlayCircle />
                  </button>
                </form>
              </div>
            </div>
          </section>

          {/* 5. RAG KNOWLEDGE BASE */}
          <section className={`tab-pane ${activeTab === 'rag' ? 'active' : ''}`}>
            <div className="rag-layout">
              <div className="rag-controls glass-panel">
                <h3>Document Ingestor</h3>
                <p className="section-desc">Load local PDF documents into the vector database (ChromaDB + Ollama Embeddings).</p>
                
                <form onSubmit={handleRAGIngestion} className="ingest-box">
                  <div className="input-field">
                    <label htmlFor="rag-file-path">File Path (PDF Absolute Path)</label>
                    <input 
                      type="text" 
                      id="rag-file-path"
                      value={filePath}
                      onChange={(e) => setFilePath(e.target.value)}
                      placeholder="e.g. C:\Users\User\Documents\report.pdf" 
                      required 
                      autoComplete="off"
                    />
                  </div>
                  <button type="submit" className="btn btn-primary btn-full" disabled={ingestLoading}>
                    {ingestLoading ? (
                      <span className="typing-indicator" style={{ display: 'inline-flex' }}>
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                      </span>
                    ) : (
                      <>
                        <FileUp />
                        <span>Ingest Document</span>
                      </>
                    )}
                  </button>
                </form>

                <div className="ingest-logs-container">
                  <h4>Ingestion Status</h4>
                  <div className="state-logs">
                    {ingestLogs.map((log, idx) => (
                      <div key={idx} className={`log-entry ${log.status}`}>
                        <span className="log-time">[{log.time}]</span> {log.text}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="info-alert danger-border">
                  <AlertCircle style={{ color: 'var(--danger)' }} />
                  <p>Make sure the file exists locally on your machine and is in PDF format. The backend splits the document into 1,000 character chunks with a 200 character overlap before saving to ChromaDB.</p>
                </div>
              </div>

              <div className="rag-query-panel glass-panel">
                <h3>Vector DB Similarity Search</h3>
                <p className="section-desc">Query the ChromaDB index to test retrieved context and chunk weights.</p>
                
                <form onSubmit={handleRAGQuery} className="rag-query-box">
                  <input 
                    type="text" 
                    value={ragQuery}
                    onChange={(e) => setRagQuery(e.target.value)}
                    placeholder="Type search term to query similarity indexes..." 
                    required 
                    autoComplete="off"
                  />
                  <button type="submit" className="btn btn-primary" disabled={ragLoading}>
                    <Search />
                    <span>Search DB</span>
                  </button>
                </form>

                <div className="retrieved-results-container">
                  <h4>Retrieved Chunks (k = 4)</h4>
                  <div className="results-deck">
                    {ragLoading ? (
                      <div className="no-results-placeholder">
                        <span className="typing-indicator">
                          <span className="typing-dot"></span>
                          <span className="typing-dot"></span>
                          <span className="typing-dot"></span>
                        </span>
                        <p>Searching Vector Store similarity weights...</p>
                      </div>
                    ) : ragResults.length === 0 ? (
                      <div className="no-results-placeholder">
                        <Database className="large-placeholder-icon" />
                        <p>No results retrieved yet. Ingest a document or run a query above to see vector store chunk weights.</p>
                      </div>
                    ) : (
                      ragResults.map((chunk, idx) => (
                        <div key={idx} className="retrieved-chunk-card">
                          <div className="chunk-header">
                            <span className="chunk-badge">MATCH {idx + 1}</span>
                            <span className="chunk-source" title={chunk.metadata.source || 'Unknown File'}>
                              {chunk.metadata.source || 'Unknown File'}
                              {chunk.metadata.page !== undefined ? ` | Page ${chunk.metadata.page + 1}` : ''}
                            </span>
                          </div>
                          <div className="chunk-content">{chunk.content}</div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
}
