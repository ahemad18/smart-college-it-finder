import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4">
      <div className="text-center space-y-6 max-w-xl">

        {/* Logo / Title */}
        <div className="space-y-2">
          <h1 className="text-4xl sm:text-5xl font-extrabold bg-gradient-to-r from-indigo-400 via-sky-400 to-emerald-400 bg-clip-text text-transparent">
            Ontario College
          </h1>
          <h1 className="text-4xl sm:text-5xl font-extrabold bg-gradient-to-r from-indigo-400 via-sky-400 to-emerald-400 bg-clip-text text-transparent">
            IT Programs
          </h1>
          <p className="text-gray-500 text-base mt-3">
            Explore and compare IT programs across 26 Ontario colleges side by side.
          </p>
        </div>

        {/* CTA Button */}
        <button
          type="button"
          onClick={() => navigate('/compare')}
          className="inline-flex items-center gap-3 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-bold text-lg px-8 py-4 rounded-2xl shadow-lg shadow-indigo-900/40 transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-gray-950"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Compare Colleges
        </button>

        {/* Stats row */}
        <div className="flex justify-center gap-8 pt-4">
          {[
            { value: '26', label: 'Colleges' },
            { value: '327', label: 'IT Programs' },
            { value: '3273', label: 'Total Programs' },
          ].map(({ value, label }) => (
            <div key={label} className="text-center">
              <p className="text-2xl font-extrabold text-indigo-400">{value}</p>
              <p className="text-xs text-gray-500 uppercase tracking-widest mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
