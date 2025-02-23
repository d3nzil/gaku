import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import "./index.css";
import App from './App.tsx'
import { CommonStateProvider } from './components/CommonState.tsx'
import { ThemeProvider } from './components/Theme.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <CommonStateProvider>
        <App />
      </CommonStateProvider>
    </ThemeProvider>
  </StrictMode>
)
