import type { FC } from 'react'
import { NavLink } from '../../router'

interface NavStep {
  path: string
  stepNumber: number
  label: string
  description: string
  end?: boolean
}

const navSteps: NavStep[] = [
  {
    path: '/',
    stepNumber: 1,
    label: 'Campaign',
    description: 'Setup campaign details',
    end: true,
  },
  {
    path: '/journalists',
    stepNumber: 2,
    label: 'Journalists',
    description: 'Import & list contacts',
    end: true,
  },
  {
    path: '/analysis',
    stepNumber: 3,
    label: 'Analysis',
    description: 'AI relevance & ranking',
    end: true,
  },
  {
    path: '/journalists/details',
    stepNumber: 4,
    label: 'Journalist Details',
    description: 'Inspect profile & evidence',
    end: true,
  },
  {
    path: '/pitch',
    stepNumber: 5,
    label: 'Pitch',
    description: 'Personalized outreach',
    end: true,
  },
]

export const Navbar: FC = () => {
  return (
    <nav className="workflow-nav" aria-label="Campaign workflow steps">
      <div className="nav-steps-container">
        {navSteps.map((step) => (
          <NavLink
            key={step.path}
            to={step.path}
            end={step.end}
            className="nav-step-item"
            activeClassName="active"
          >
            <span className="step-badge">{step.stepNumber}</span>
            <div className="step-meta">
              <span className="step-label">{step.label}</span>
              <span className="step-desc">{step.description}</span>
            </div>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
