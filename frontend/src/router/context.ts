import { createContext, useContext } from 'react'

export interface RouterContextType {
  pathname: string
  navigate: (to: string) => void
  params: Record<string, string>
}

export const RouterContext = createContext<RouterContextType>({
  pathname: window.location.pathname || '/',
  navigate: () => {},
  params: {},
})

export function useNavigate() {
  const context = useContext(RouterContext)
  return context.navigate
}

export function useLocation() {
  const context = useContext(RouterContext)
  return { pathname: context.pathname }
}

export function useParams(): Record<string, string> {
  const context = useContext(RouterContext)
  return context.params
}
