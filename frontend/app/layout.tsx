import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpsPilot AI — AI Decision Engine for Compliance Operations",
  description:
    "Policy-grounded AI decision infrastructure for compliance-critical operational workflows. RAG-powered case review with agentic orchestration, evaluation, and full trace logging.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <nav className="navbar">
          <div className="navbar-inner">
            <a href="/" className="navbar-logo">
              <div className="navbar-logo-icon">⬡</div>
              OpsPilot AI
            </a>
            <div className="navbar-links">
              <a href="/review" className="navbar-link">
                Case Review
              </a>
              <a href="/traces" className="navbar-link">
                Trace History
              </a>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
