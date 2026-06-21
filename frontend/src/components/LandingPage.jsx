import React from 'react';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../authConfig';
import './LandingPage.css';

export default function LandingPage() {
  const { instance } = useMsal();

  const handleLogin = () => {
    // loginRedirect navigates to the Microsoft login page, then returns here
    instance.loginRedirect(loginRequest).catch(e => console.error(e));
  };

  return (
    <div className="landing-layout">
      {/* Navbar */}
      <nav className="landing-nav">
        <div className="landing-brand">
          <div className="landing-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="url(#logoGradient)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#22d3ee" />
                </linearGradient>
              </defs>
              <path d="M12 8V4H8" />
              <rect width="16" height="12" x="4" y="8" rx="2" />
              <path d="M2 14h2" />
              <path d="M20 14h2" />
              <path d="M15 13v2" />
              <path d="M9 13v2" />
            </svg>
          </div>
          <span className="landing-brand-text">Enterprise AI</span>
        </div>
        <button className="landing-nav-signin" onClick={handleLogin}>
          Sign In
        </button>
      </nav>

      {/* Hero Section */}
      <header className="landing-hero">
        <div className="hero-background">
          <div className="hero-orb orb-1" />
          <div className="hero-orb orb-2" />
        </div>
        <div className="hero-content">
          <div className="hero-badge">✨ Next-Generation AI Assistant</div>
          <h1 className="hero-title">
            Empower Your Team with <br />
            <span className="text-gradient">Intelligent Agents</span>
          </h1>
          <p className="hero-subtitle">
            Secure, scalable, and fully integrated with your corporate identity. 
            Experience multi-agent orchestration designed specifically for enterprise workflows.
          </p>
          <div className="hero-actions">
            <button className="hero-primary-btn" onClick={handleLogin}>
              Get Started securely
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className="landing-features">
        <div className="feature-card">
          <div className="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
          <h3>Enterprise Security</h3>
          <p>Seamlessly integrated with Azure Active Directory. Complete data isolation and RBAC access controls natively built-in.</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="2" y1="12" x2="22" y2="12" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
          </div>
          <h3>Multi-Agent Swarms</h3>
          <p>Go beyond simple chatbots. Deploy specialized agent swarms that collaborate to solve complex, multi-step problems.</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
              <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
              <line x1="12" y1="22.08" x2="12" y2="12" />
            </svg>
          </div>
          <h3>RAG Integrations</h3>
          <p>Connect securely to your proprietary data stores, documentation, and databases for highly contextual and accurate answers.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="landing-logo">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="url(#logoGradient)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 8V4H8" />
                <rect width="16" height="12" x="4" y="8" rx="2" />
                <path d="M2 14h2" />
                <path d="M20 14h2" />
                <path d="M15 13v2" />
                <path d="M9 13v2" />
              </svg>
            </div>
            <span className="landing-brand-text">Enterprise AI</span>
            <p className="footer-description">
              Next-generation multi-agent orchestration for modern enterprise workflows. Secure, scalable, and deeply integrated.
            </p>
          </div>
          
          <div className="footer-links">
            <div className="footer-column">
              <h4>Product</h4>
              <a href="#">Agent Swarms</a>
              <a href="#">RAG Integrations</a>
              <a href="#">Security & Compliance</a>
              <a href="#">Pricing</a>
            </div>
            <div className="footer-column">
              <h4>Resources</h4>
              <a href="#">Documentation</a>
              <a href="#">API Reference</a>
              <a href="#">Community Forum</a>
              <a href="#">Blog</a>
            </div>
            <div className="footer-column">
              <h4>Company</h4>
              <a href="#">About Us</a>
              <a href="#">Careers</a>
              <a href="#">Contact Sales</a>
              <a href="#">Partners</a>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} Enterprise AI. All rights reserved.</p>
          <div className="footer-legal">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Cookie Policy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
