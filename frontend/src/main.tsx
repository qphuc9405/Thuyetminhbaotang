import { createRoot } from 'react-dom/client';
import App from './App';
import './style.css';
import './responsive.css';
import './zones.css';
import './hall.css';
import './camera.css';
import './guide.css';
import './museum-topics.css';
import './toolbar.css';

createRoot(document.getElementById('root')!).render(<App />);
