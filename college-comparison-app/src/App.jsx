import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import CollegeComparison from './CollegeComparison';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/compare" element={<CollegeComparison />} />
      </Routes>
    </BrowserRouter>
  );
}

