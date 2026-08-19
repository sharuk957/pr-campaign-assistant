import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { RouterContext, useLocation, useNavigate } from './context'

export function BrowserRouter({ children }: { children: React.ReactNode }) {
  const [pathname, setPathname] = useState<string>(() => window.location.pathname || '/')
  const [params, setParams] = useState<Record<string, string>>({})

  useEffect(() => {
    const handlePopState = () => {
      setPathname(window.location.pathname || '/')
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const navigate = useCallback((to: string) => {
    setPathname((current) => {
      if (to === current) return current
      window.history.pushState(null, '', to)
      window.scrollTo(0, 0)
      return to
    })
  }, [])

  const value = useMemo(
    () => ({
      pathname,
      navigate,
      params,
      setParams,
    }),
    [pathname, navigate, params]
  )

  return (
    <RouterContext.Provider value={value}>
      {children}
    </RouterContext.Provider>
  )
}

interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  to: string
  children: React.ReactNode
}

export function Link({ to, children, className, onClick, ...rest }: LinkProps) {
  const navigate = useNavigate()

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (onClick) onClick(e)
    if (!e.defaultPrevented && e.button === 0 && !e.metaKey && !e.ctrlKey && !e.altKey && !e.shiftKey) {
      e.preventDefault()
      navigate(to)
    }
  }

  return (
    <a href={to} className={className} onClick={handleClick} {...rest}>
      {children}
    </a>
  )
}

interface NavLinkProps extends LinkProps {
  activeClassName?: string
  end?: boolean
}

export function NavLink({
  to,
  children,
  className = '',
  activeClassName = 'active',
  end = false,
  ...rest
}: NavLinkProps) {
  const { pathname } = useLocation()
  const isActive = end ? pathname === to : pathname === to || (to !== '/' && pathname.startsWith(to))

  const combinedClassName = [className, isActive ? activeClassName : ''].filter(Boolean).join(' ')

  return (
    <Link to={to} className={combinedClassName} {...rest}>
      {children}
    </Link>
  )
}

export interface RouteProps {
  path: string
  element: React.ReactNode
}

export function Route({ element }: RouteProps) {
  return <>{element}</>
}

function matchPath(pattern: string, pathname: string): { matched: boolean; params: Record<string, string> } {
  if (pattern === pathname) {
    return { matched: true, params: {} }
  }

  if (pattern === '*') {
    return { matched: true, params: {} }
  }

  const patternSegments = pattern.split('/').filter(Boolean)
  const pathnameSegments = pathname.split('/').filter(Boolean)

  if (patternSegments.length !== pathnameSegments.length) {
    return { matched: false, params: {} }
  }

  const params: Record<string, string> = {}
  for (let i = 0; i < patternSegments.length; i++) {
    const p = patternSegments[i]
    const u = pathnameSegments[i]

    if (p.startsWith(':')) {
      params[p.slice(1)] = decodeURIComponent(u)
    } else if (p !== u) {
      return { matched: false, params: {} }
    }
  }

  return { matched: true, params }
}

export function Routes({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  const context = React.useContext(RouterContext)

  const childrenArray = React.Children.toArray(children) as React.ReactElement<RouteProps>[]

  for (const child of childrenArray) {
    if (React.isValidElement<RouteProps>(child)) {
      const { path, element } = child.props
      const { matched, params } = matchPath(path, pathname)
      if (matched) {
        if (JSON.stringify(context.params) !== JSON.stringify(params)) {
          setTimeout(() => {
            if ((context as unknown as { setParams?: (p: Record<string, string>) => void }).setParams) {
              (context as unknown as { setParams: (p: Record<string, string>) => void }).setParams(params)
            }
          }, 0)
        }
        return <>{element}</>
      }
    }
  }

  return null
}
