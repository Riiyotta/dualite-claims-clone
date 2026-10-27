import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './index.css';

// No StrictMode: the motion layer mutates the DOM directly and must boot exactly once.
createRoot(document.getElementById('root')).render(<App />);
