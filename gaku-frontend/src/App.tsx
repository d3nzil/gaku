import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CardEditor from "./components/pages/CardEditor"; // Adjust the path based on where you saved CardEditor.js
import Navigation from "./components/Navigation";
import TestFlashcards from "./components/pages/TestFlashCards"; // Adjust the path based on where you saved TestFlashcards.js
import DisplayResults from "./components/pages/DisplayResults";
import SourcesEditor from "./components/pages/SourcesEditor"; // Adjust the path based on where you saved SourceEditor.js
import ImportTool from "./components/pages/ImportTool";
import SelectTest from "./components/pages/SelectTest"; // Adjust the path based on where you saved SelectTest.js
import MultiCardEditor from "./components/pages/multiCardEditor";
import CardManager from './components/pages/CardManager';

function App() {
  return (
    <Router>
      <Navigation />
      <Routes>
        <Route path='/cardmanager' element={<CardManager />} />
        <Route path="/cards" element={<CardEditor />} /> {/* Default route */}
        <Route path="/source" element={<SourcesEditor />} />
        {/* <Route path="/edit" element={<EditFlashcards />} /> */}
        <Route path="/" element={<SelectTest />} />
        <Route path="/test" element={<TestFlashcards />} />
        <Route path="/results" element={<DisplayResults />} />
        <Route path="/import" element={<ImportTool />} />
        <Route path="/multi" element={<MultiCardEditor />} />
      </Routes>
    </Router>
  );
}

export default App;
