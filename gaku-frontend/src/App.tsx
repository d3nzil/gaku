import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from "./components/Navigation";
import TestFlashcards from "./components/pages/TestFlashCards"; // Adjust the path based on where you saved TestFlashcards.js
import DisplayResults from "./components/pages/DisplayResults";
import SelectTest from "./components/pages/SelectTest"; // Adjust the path based on where you saved SelectTest.js
import CardManager from './components/pages/CardManager';

function App() {
  return (
    <Router>
      <Navigation />
      <Routes>
        <Route path='/cardmanager' element={<CardManager />} />
        <Route path="/" element={<SelectTest />} />
        <Route path="/test" element={<TestFlashcards />} />
        <Route path="/results" element={<DisplayResults />} />
      </Routes>
    </Router>
  );
}

export default App;
