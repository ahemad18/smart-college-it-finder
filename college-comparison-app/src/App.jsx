import { HashRouter, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import CollegeComparison from './CollegeComparison';

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/compare" element={<CollegeComparison />} />
      </Routes>
    </HashRouter>
  );
}

