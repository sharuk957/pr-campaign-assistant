import type { FC, ReactNode } from 'react'
import { Header } from './Header'
import { Navbar } from './Navbar'

interface LayoutProps {
  children: ReactNode
}

export const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <div className="app-shell">
      <Header />
      <Navbar />
      <main className="app-main-content">
        <div className="content-container">
          {children}
        </div>
      </main>
      <footer className="app-footer">
        <div className="footer-content">
          <p>PR Campaign Assistant &mdash; AI-Powered Media Outreach</p>
          <span className="footer-divider">&bull;</span>
          <p className="footer-subtitle">Modular Monolith Architecture</p>
        </div>
      </footer>
    </div>
  )
}
