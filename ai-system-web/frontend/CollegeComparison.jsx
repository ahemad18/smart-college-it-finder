/**
 * CollegeComparison.jsx
 *
 * A fully interactive college comparison section.
 * Compares 3–5 colleges across 5 key metrics with 4 charts.
 *
 * Dependencies:
 *   npm install recharts
 *   (Tailwind CSS must be configured in your project)
 *
 * Usage:
 *   import CollegeComparison from './CollegeComparison';
 *   <CollegeComparison />
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, LineChart, Line,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell,
} from 'recharts';

/* ═══════════════════════════════════════════════════════════════════════
   STATIC DATA
   Source: ontario_college_IT_programs_ONLY_DEDUP_COLLEGE_PROGRAM.csv
   itPrograms / totalPrograms are real counts from the dataset.
   fees, placementRate, avgSalary, salaryTrend, studentRating, infraScore
   are representative estimates for Ontario college IT programs.
   ═══════════════════════════════════════════════════════════════════════ */

const PALETTE = [
  '#6366f1', // indigo
  '#0ea5e9', // sky
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ec4899', // pink
  '#8b5cf6', // violet
  '#f97316', // orange
  '#14b8a6', // teal
];

const YEARS = [2020, 2021, 2022, 2023, 2024];

/**
 * COLLEGE_POOL — top 10 Ontario colleges ranked by IT program count.
 * itPrograms / totalPrograms come directly from the CSV dataset.
 */
const COLLEGE_POOL = [
  {
    id: 1,
    name: 'Sheridan',
    fees: 8200,
    placementRate: 92,
    avgSalary: 65000,
    salaryTrend: [55000, 58000, 61000, 63000, 65000],
    studentRating: 4.3,
    infraScore: 82,
    itPrograms: 38,
    totalPrograms: 178,
  },
  {
    id: 2,
    name: 'Conestoga',
    fees: 7800,
    placementRate: 94,
    avgSalary: 68000,
    salaryTrend: [57000, 60000, 63000, 65500, 68000],
    studentRating: 4.4,
    infraScore: 85,
    itPrograms: 32,
    totalPrograms: 275,
  },
  {
    id: 3,
    name: 'Seneca',
    fees: 7500,
    placementRate: 91,
    avgSalary: 64000,
    salaryTrend: [54000, 57000, 59500, 62000, 64000],
    studentRating: 4.1,
    infraScore: 78,
    itPrograms: 31,
    totalPrograms: 229,
  },
  {
    id: 4,
    name: 'Centennial',
    fees: 7200,
    placementRate: 89,
    avgSalary: 63000,
    salaryTrend: [53000, 56000, 58500, 61000, 63000],
    studentRating: 4.0,
    infraScore: 76,
    itPrograms: 25,
    totalPrograms: 172,
  },
  {
    id: 5,
    name: 'George Brown',
    fees: 7900,
    placementRate: 93,
    avgSalary: 66000,
    salaryTrend: [55500, 58500, 61500, 64000, 66000],
    studentRating: 4.2,
    infraScore: 80,
    itPrograms: 24,
    totalPrograms: 149,
  },
  {
    id: 6,
    name: 'Humber',
    fees: 7600,
    placementRate: 90,
    avgSalary: 64000,
    salaryTrend: [54500, 57000, 60000, 62500, 64000],
    studentRating: 4.1,
    infraScore: 79,
    itPrograms: 19,
    totalPrograms: 212,
  },
  {
    id: 7,
    name: 'Fanshawe',
    fees: 6800,
    placementRate: 88,
    avgSalary: 62000,
    salaryTrend: [52000, 55000, 57500, 60000, 62000],
    studentRating: 4.0,
    infraScore: 74,
    itPrograms: 19,
    totalPrograms: 264,
  },
  {
    id: 8,
    name: 'Algonquin',
    fees: 7100,
    placementRate: 91,
    avgSalary: 65000,
    salaryTrend: [55000, 58000, 60500, 63000, 65000],
    studentRating: 4.2,
    infraScore: 77,
    itPrograms: 18,
    totalPrograms: 184,
  },
  {
    id: 9,
    name: 'Cambrian',
    fees: 5900,
    placementRate: 87,
    avgSalary: 58000,
    salaryTrend: [48000, 51000, 53500, 56000, 58000],
    studentRating: 3.9,
    infraScore: 70,
    itPrograms: 18,
    totalPrograms: 148,
  },
  {
    id: 10,
    name: 'Georgian',
    fees: 6600,
    placementRate: 88,
    avgSalary: 60000,
    salaryTrend: [50000, 53000, 55500, 58000, 60000],
    studentRating: 3.9,
    infraScore: 72,
    itPrograms: 17,
    totalPrograms: 178,
  },
  {
    id: 11,
    name: 'Boréal',
    fees: 5800,
    placementRate: 85,
    avgSalary: 57000,
    salaryTrend: [47000, 49500, 52000, 54500, 57000],
    studentRating: 3.8,
    infraScore: 68,
    itPrograms: 4,
    totalPrograms: 51,
  },
  {
    id: 12,
    name: 'Canadore',
    fees: 6000,
    placementRate: 86,
    avgSalary: 58000,
    salaryTrend: [48000, 50500, 53000, 55500, 58000],
    studentRating: 3.8,
    infraScore: 69,
    itPrograms: 7,
    totalPrograms: 95,
  },
  {
    id: 13,
    name: 'Confederation',
    fees: 5700,
    placementRate: 84,
    avgSalary: 56000,
    salaryTrend: [46000, 48500, 51000, 53500, 56000],
    studentRating: 3.7,
    infraScore: 67,
    itPrograms: 3,
    totalPrograms: 81,
  },
  {
    id: 14,
    name: 'Durham',
    fees: 7000,
    placementRate: 89,
    avgSalary: 62000,
    salaryTrend: [52000, 54500, 57000, 59500, 62000],
    studentRating: 4.0,
    infraScore: 75,
    itPrograms: 11,
    totalPrograms: 173,
  },
  {
    id: 15,
    name: 'Fleming',
    fees: 6500,
    placementRate: 87,
    avgSalary: 59000,
    salaryTrend: [49000, 51500, 54000, 56500, 59000],
    studentRating: 3.9,
    infraScore: 71,
    itPrograms: 4,
    totalPrograms: 87,
  },
  {
    id: 16,
    name: 'La Cité',
    fees: 7200,
    placementRate: 88,
    avgSalary: 61000,
    salaryTrend: [51000, 53500, 56000, 58500, 61000],
    studentRating: 4.0,
    infraScore: 74,
    itPrograms: 14,
    totalPrograms: 138,
  },
  {
    id: 17,
    name: 'Lambton',
    fees: 6200,
    placementRate: 86,
    avgSalary: 57000,
    salaryTrend: [47000, 49500, 52000, 54500, 57000],
    studentRating: 3.8,
    infraScore: 70,
    itPrograms: 5,
    totalPrograms: 77,
  },
  {
    id: 18,
    name: 'Loyalist',
    fees: 6100,
    placementRate: 85,
    avgSalary: 56000,
    salaryTrend: [46000, 48500, 51000, 53500, 56000],
    studentRating: 3.8,
    infraScore: 68,
    itPrograms: 2,
    totalPrograms: 59,
  },
  {
    id: 19,
    name: 'Michener',
    fees: 7800,
    placementRate: 93,
    avgSalary: 65000,
    salaryTrend: [55000, 57500, 60000, 62500, 65000],
    studentRating: 4.3,
    infraScore: 82,
    itPrograms: 0,
    totalPrograms: 11,
  },
  {
    id: 20,
    name: 'Mohawk',
    fees: 7000,
    placementRate: 89,
    avgSalary: 62000,
    salaryTrend: [52000, 54500, 57000, 59500, 62000],
    studentRating: 4.0,
    infraScore: 75,
    itPrograms: 8,
    totalPrograms: 109,
  },
  {
    id: 21,
    name: 'Niagara',
    fees: 6800,
    placementRate: 88,
    avgSalary: 60000,
    salaryTrend: [50000, 52500, 55000, 57500, 60000],
    studentRating: 3.9,
    infraScore: 73,
    itPrograms: 8,
    totalPrograms: 123,
  },
  {
    id: 22,
    name: 'Northern',
    fees: 5500,
    placementRate: 83,
    avgSalary: 54000,
    salaryTrend: [44000, 46500, 49000, 51500, 54000],
    studentRating: 3.7,
    infraScore: 65,
    itPrograms: 2,
    totalPrograms: 49,
  },
  {
    id: 23,
    name: 'Ridgetown Campus',
    fees: 5400,
    placementRate: 82,
    avgSalary: 52000,
    salaryTrend: [42000, 44500, 47000, 49500, 52000],
    studentRating: 3.6,
    infraScore: 63,
    itPrograms: 0,
    totalPrograms: 11,
  },
  {
    id: 24,
    name: 'Sault',
    fees: 5800,
    placementRate: 85,
    avgSalary: 55000,
    salaryTrend: [45000, 47500, 50000, 52500, 55000],
    studentRating: 3.7,
    infraScore: 67,
    itPrograms: 3,
    totalPrograms: 54,
  },
  {
    id: 25,
    name: 'St. Clair',
    fees: 6700,
    placementRate: 88,
    avgSalary: 61000,
    salaryTrend: [51000, 53500, 56000, 58500, 61000],
    studentRating: 4.0,
    infraScore: 73,
    itPrograms: 7,
    totalPrograms: 85,
  },
  {
    id: 26,
    name: 'St. Lawrence',
    fees: 6400,
    placementRate: 87,
    avgSalary: 59000,
    salaryTrend: [49000, 51500, 54000, 56500, 59000],
    studentRating: 3.9,
    infraScore: 71,
    itPrograms: 8,
    totalPrograms: 81,
  },
];



/* ═══════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════ */

const colorAt  = (i) => PALETTE[i % PALETTE.length];
const fmtMoney = (v) => `$${Number(v).toLocaleString()}`;
const fmtPct   = (v) => `${v}%`;
const fmtStars = (v) => `${v} / 5`;
const fmtScore = (v) => `${v} / 100`;

/**
 * Maps `value` into a 40–100 range relative to `allValues`.
 * invertBetter: true means LOWER value = BETTER score (e.g. fees).
 */
function normalizeInRange(value, allValues, invertBetter = false) {
  const min = Math.min(...allValues);
  const max = Math.max(...allValues);
  if (max === min) return 70;
  const ratio = (value - min) / (max - min);
  return Math.round((invertBetter ? 1 - ratio : ratio) * 60 + 40);
}

/* ═══════════════════════════════════════════════════════════════════════
   CUSTOM RECHARTS TOOLTIP
   ═══════════════════════════════════════════════════════════════════════ */

function ChartTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  const isMulti = payload.length > 1;

  return (
    <div className="bg-[#0f172a] border border-gray-700 rounded-xl px-4 py-3 shadow-2xl text-sm min-w-[160px]">
      {label && (
        <p className="text-gray-400 text-[10px] uppercase tracking-widest font-semibold mb-2 pb-1.5 border-b border-gray-700">
          {label}
        </p>
      )}

      <div className="space-y-1.5">
        {payload.map((entry, i) => {
          const color = entry.payload?.fill ?? entry.color ?? entry.stroke ?? '#fff';
          return (
            <div key={i} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ background: color }}
                />
                {isMulti && (
                  <span className="text-gray-400 text-xs whitespace-nowrap">{entry.name}</span>
                )}
              </div>
              <span className="text-white font-bold text-xs whitespace-nowrap">
                {formatter ? formatter(entry.value) : entry.value}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
   CHART SECTION WRAPPER
   ═══════════════════════════════════════════════════════════════════════ */

function ChartCard({ title, accentColor, children }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
      <h3 className="text-gray-300 text-[11px] font-semibold uppercase tracking-widest mb-4 flex items-center gap-2">
        <span
          className="w-1 h-4 rounded-sm inline-block flex-shrink-0"
          style={{ background: accentColor }}
        />
        {title}
      </h3>
      {children}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
   MAIN COMPONENT
   ═══════════════════════════════════════════════════════════════════════ */

// Resolve the API base so this component works whether served via FastAPI
// or embedded inside the college-comparison-app Vite dev server.
const API_BASE = typeof window !== 'undefined'
  ? (window.location.port && window.location.port !== '8000'
      ? 'http://localhost:8000'
      : window.location.origin)
  : 'http://localhost:8000';

export default function CollegeComparison() {
  const [selectedIds, setSelectedIds] = useState([1, 2, 3]);
  const [dropOpen, setDropOpen]       = useState(false);
  const [apiData, setApiData]         = useState({});   // keyed by college name: { it_programs, total_programs, ... }
  const [apiLoading, setApiLoading]   = useState(false);

  /* Derived list of selected college objects (always 3–5) */
  const selected = useMemo(
    () => COLLEGE_POOL.filter((c) => selectedIds.includes(c.id)),
    [selectedIds],
  );

  /* Fetch real IT program counts whenever the selection changes */
  useEffect(() => {
    if (selected.length < 2) return;
    setApiLoading(true);
    const names = selected.map((c) => encodeURIComponent(c.name)).join(',');
    fetch(`${API_BASE}/api/compare-colleges?colleges=${names}`)
      .then((r) => r.ok ? r.json() : Promise.reject(r.status))
      .then((data) => {
        const map = {};
        if (data.colleges) {
          data.colleges.forEach((c) => { map[c.college] = c; });
        }
        setApiData(map);
        setApiLoading(false);
      })
      .catch(() => setApiLoading(false));   // graceful degradation: keep static estimates
  }, [selectedIds.join(',')]);

  /* Merge live API counts (itPrograms, totalPrograms) into each college record */
  const selectedWithLiveData = useMemo(
    () => selected.map((c) => {
      const live = apiData[c.name];
      if (!live) return c;
      return {
        ...c,
        itPrograms:    live.it_programs    ?? c.itPrograms,
        totalPrograms: live.total_programs ?? c.totalPrograms,
      };
    }),
    [selected, apiData],
  );

  /* Toggle a college in/out (min 3, max 5) */
  const toggle = useCallback((id) => {
    setSelectedIds((prev) =>
      prev.includes(id)
        ? prev.length > 3 ? prev.filter((x) => x !== id) : prev
        : prev.length < 5 ? [...prev, id] : prev,
    );
  }, []);


  const colorOf = (college) => colorAt(selectedWithLiveData.findIndex((c) => c.id === college.id));

  /* ── Chart data ──────────────────────────────────────────────────── */

  const feesData = useMemo(
    () => selectedWithLiveData.map((c, i) => ({ name: c.name, fees: c.fees, fill: colorAt(i) })),
    [selectedWithLiveData],
  );

  const placementData = useMemo(
    () => selectedWithLiveData.map((c, i) => ({ name: c.name, rate: c.placementRate, fill: colorAt(i) })),
    [selectedWithLiveData],
  );

  const salaryTrendData = useMemo(
    () => YEARS.map((year, yi) => ({
      year,
      ...selectedWithLiveData.reduce((acc, c) => ({ ...acc, [c.name]: c.salaryTrend[yi] }), {}),
    })),
    [selectedWithLiveData],
  );

  const radarData = useMemo(() => {
    const norm = (key, invert = false) => {
      const vals = selectedWithLiveData.map((c) => c[key]);
      return selectedWithLiveData.reduce(
        (acc, c) => ({ ...acc, [c.name]: normalizeInRange(c[key], vals, invert) }),
        {},
      );
    };
    return [
      { metric: 'IT Programs',   ...norm('itPrograms'),          fullMark: 100 },
      { metric: 'Placement',     ...norm('placementRate'),       fullMark: 100 },
      { metric: 'Avg Salary',    ...norm('avgSalary'),           fullMark: 100 },
      { metric: 'Affordability', ...norm('fees', true),          fullMark: 100 },
      { metric: 'Rating',        ...norm('studentRating'),       fullMark: 100 },
      { metric: 'Infrastructure',...norm('infraScore'),          fullMark: 100 },
    ];
  }, [selectedWithLiveData]);

  /* ── Best performer per metric ──────────────────────────────────── */

  const bests = useMemo(() => [
    {
      label: 'Most IT Programs', icon: '💻',
      college: selectedWithLiveData.reduce((b, c) => (c.itPrograms > b.itPrograms ? c : b), selectedWithLiveData[0]),
      fmt: (c) => `${c.itPrograms} programs`,
    },
    {
      label: 'Lowest Fees',     icon: '💸',
      college: selectedWithLiveData.reduce((b, c) => (c.fees < b.fees ? c : b), selectedWithLiveData[0]),
      fmt: (c) => fmtMoney(c.fees),
    },
    {
      label: 'Placement Rate',  icon: '🎓',
      college: selectedWithLiveData.reduce((b, c) => (c.placementRate > b.placementRate ? c : b), selectedWithLiveData[0]),
      fmt: (c) => fmtPct(c.placementRate),
    },
    {
      label: 'Avg Salary',      icon: '💰',
      college: selectedWithLiveData.reduce((b, c) => (c.avgSalary > b.avgSalary ? c : b), selectedWithLiveData[0]),
      fmt: (c) => fmtMoney(c.avgSalary),
    },
    {
      label: 'Student Rating',  icon: '⭐',
      college: selectedWithLiveData.reduce((b, c) => (c.studentRating > b.studentRating ? c : b), selectedWithLiveData[0]),
      fmt: (c) => fmtStars(c.studentRating),
    },
  ], [selectedWithLiveData]);

  /* ── Render ──────────────────────────────────────────────────────── */

  return (
    <section className="bg-gray-950 text-white px-4 py-12 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* ── Page Header ───────────────────────────────────────────── */}
        <div className="text-center space-y-2">
          <h2 className="text-3xl sm:text-4xl font-extrabold bg-gradient-to-r from-indigo-400 via-sky-400 to-emerald-400 bg-clip-text text-transparent">
            College Comparison
          </h2>
          <p className="text-gray-500 text-sm">
            Compare 3–5 colleges side by side across key metrics
          </p>
          {apiLoading && (
            <p className="text-sky-400 text-xs animate-pulse">Loading live IT program data…</p>
          )}
        </div>

        {/* ── College Selector ──────────────────────────────────────── */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 space-y-4">

          {/* Selected chips */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-gray-500 text-xs font-medium shrink-0">
              Selected ({selectedIds.length}/5):
            </span>

            {selectedWithLiveData.map((c, i) => (
              <span
                key={c.id}
                className="inline-flex items-center gap-1.5 text-sm font-semibold px-3 py-1 rounded-full"
                style={{
                  background: `${colorAt(i)}1a`,
                  border: `1.5px solid ${colorAt(i)}66`,
                  color: colorAt(i),
                }}
              >
                {c.name}
                {selectedIds.length > 3 && (
                  <button
                    type="button"
                    onClick={() => toggle(c.id)}
                    className="ml-0.5 opacity-50 hover:opacity-100 transition-opacity text-xs leading-none"
                    aria-label={`Remove ${c.name}`}
                  >
                    ✕
                  </button>
                )}
              </span>
            ))}
          </div>

          {/* Dropdown */}
          <div className="relative inline-block">
            <button
              type="button"
              onClick={() => setDropOpen((v) => !v)}
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              ＋ Add / Remove College
              <svg
                className={`w-4 h-4 transition-transform duration-200 ${dropOpen ? 'rotate-180' : ''}`}
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {dropOpen && (
              <>
                {/* Backdrop to close on outside click */}
                <div className="fixed inset-0 z-40" onClick={() => setDropOpen(false)} />

                <ul className="absolute top-full mt-2 left-0 z-50 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl w-56 py-1 overflow-hidden">
                  {COLLEGE_POOL.map((c) => {
                    const isSel    = selectedIds.includes(c.id);
                    const selIdx   = selected.findIndex((s) => s.id === c.id);
                    const disabled = !isSel && selectedIds.length >= 5;

                    return (
                      <li key={c.id}>
                        <button
                          type="button"
                          onClick={() => toggle(c.id)}
                          disabled={disabled}
                          className={[
                            'w-full flex items-center justify-between px-4 py-2.5 text-sm text-left transition-colors',
                            isSel    ? 'bg-gray-700/50 text-white font-semibold' : 'text-gray-300',
                            disabled ? 'opacity-35 cursor-not-allowed' : 'hover:bg-gray-700/40 cursor-pointer',
                          ].join(' ')}
                        >
                          {c.name}
                          {isSel && (
                            <span
                              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                              style={{ background: colorAt(selIdx) }}
                            />
                          )}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </>
            )}
          </div>
        </div>

        {/* ── Top Performers Cards ──────────────────────────────────── */}
        <div className="space-y-3">
          <p className="text-gray-500 text-[11px] uppercase tracking-widest font-semibold">
            Top Performers
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {bests.map(({ label, college, fmt, icon }) => {
              const color = colorOf(college);
              return (
                <div
                  key={label}
                  className="relative rounded-2xl p-4 border transition-all hover:scale-[1.02]"
                  style={{ background: `${color}12`, borderColor: `${color}33` }}
                >
                  <span
                    className="absolute top-2.5 right-2.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                    style={{ background: `${color}25`, color }}
                  >
                    #1
                  </span>
                  <div className="text-2xl mb-1.5">{icon}</div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-widest leading-snug">{label}</p>
                  <p className="text-white font-bold text-sm mt-0.5 truncate">{fmt(college)}</p>
                  <p className="text-[11px] font-semibold mt-1 truncate" style={{ color }}>
                    {college.name}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Metrics Table ─────────────────────────────────────────── */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-x-auto">
          <table className="w-full text-sm min-w-[480px]">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left px-5 py-4 text-gray-500 font-medium text-xs uppercase tracking-wider">
                  Metric
                </th>
                {selectedWithLiveData.map((c, i) => (
                  <th key={c.id} className="px-4 py-4 text-center">
                    <span className="text-sm font-bold" style={{ color: colorAt(i) }}>
                      {c.name}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-800/60">
              {[
                { emoji: '💻', label: 'IT Programs (live)', key: 'itPrograms',    fmt: (v) => `${v} programs`, lowerBetter: false },
                { emoji: '📚', label: 'Total Programs',     key: 'totalPrograms', fmt: (v) => `${v} programs`, lowerBetter: false },
                { emoji: '💸', label: 'Fees / Year',        key: 'fees',          fmt: fmtMoney,  lowerBetter: true  },
                { emoji: '🎓', label: 'Placement Rate',     key: 'placementRate', fmt: fmtPct,    lowerBetter: false },
                { emoji: '💰', label: 'Avg Salary',         key: 'avgSalary',     fmt: fmtMoney,  lowerBetter: false },
                { emoji: '⭐', label: 'Student Rating',     key: 'studentRating', fmt: fmtStars,  lowerBetter: false },
                { emoji: '🏛️', label: 'Infrastructure',    key: 'infraScore',    fmt: fmtScore,  lowerBetter: false },
              ].map(({ emoji, label, key, fmt, lowerBetter }) => {
                const vals    = selectedWithLiveData.map((c) => c[key]);
                const bestVal = lowerBetter ? Math.min(...vals) : Math.max(...vals);

                return (
                  <tr key={key} className="hover:bg-gray-800/30 transition-colors">
                    <td className="px-5 py-3.5 text-gray-300 font-medium whitespace-nowrap">
                      {emoji} {label}
                    </td>
                    {selectedWithLiveData.map((c) => {
                      const isBest = c[key] === bestVal;
                      return (
                        <td key={c.id} className="px-4 py-3.5 text-center">
                          <span
                            className={`inline-block px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                              isBest
                                ? 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30'
                                : 'text-gray-400'
                            }`}
                          >
                            {isBest && <span className="mr-0.5">✓</span>}
                            {fmt(c[key])}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* ── Charts 2×2 Grid ───────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* 1. Annual Fees — Bar */}
          <ChartCard title="Annual Fees Comparison" accentColor="#6366f1">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={feesData} barCategoryGap="35%" margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false} tickLine={false}
                />
                <YAxis
                  tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false} tickLine={false} width={44}
                />
                <Tooltip content={<ChartTooltip formatter={fmtMoney} />} cursor={{ fill: '#ffffff06' }} />
                <Bar dataKey="fees" radius={[6, 6, 0, 0]} maxBarSize={60}>
                  {feesData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* 2. Placement Rate — Bar */}
          <ChartCard title="Placement Rate (%)" accentColor="#0ea5e9">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={placementData} barCategoryGap="35%" margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false} tickLine={false}
                />
                <YAxis
                  domain={[85, 100]}
                  tickFormatter={(v) => `${v}%`}
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false} tickLine={false} width={36}
                />
                <Tooltip content={<ChartTooltip formatter={fmtPct} />} cursor={{ fill: '#ffffff06' }} />
                <Bar dataKey="rate" radius={[6, 6, 0, 0]} maxBarSize={60}>
                  {placementData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* 3. Salary Trend — Line */}
          <ChartCard title="Average Salary Trend (2020–2024)" accentColor="#10b981">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={salaryTrendData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis
                  dataKey="year"
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false} tickLine={false}
                />
                <YAxis
                  tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={false} tickLine={false} width={44}
                />
                <Tooltip content={<ChartTooltip formatter={fmtMoney} />} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  formatter={(n) => <span style={{ color: '#9ca3af', fontSize: 11 }}>{n}</span>}
                />
                {selectedWithLiveData.map((c, i) => (
                  <Line
                    key={c.id}
                    type="monotone"
                    dataKey={c.name}
                    stroke={colorAt(i)}
                    strokeWidth={2.5}
                    dot={{ r: 4, fill: colorAt(i), strokeWidth: 0 }}
                    activeDot={{ r: 6, stroke: '#fff', strokeWidth: 2 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* 4. Overall Radar */}
          <ChartCard title="Overall Radar Comparison" accentColor="#f59e0b">
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart cx="50%" cy="50%" outerRadius="68%" data={radarData}>
                <PolarGrid stroke="#1f2937" />
                <PolarAngleAxis
                  dataKey="metric"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tick={false}
                  axisLine={false}
                />
                {selectedWithLiveData.map((c, i) => (
                  <Radar
                    key={c.id}
                    name={c.name}
                    dataKey={c.name}
                    stroke={colorAt(i)}
                    fill={colorAt(i)}
                    fillOpacity={0.12}
                    strokeWidth={2}
                  />
                ))}
                <Tooltip content={<ChartTooltip />} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  formatter={(n) => <span style={{ color: '#9ca3af', fontSize: 11 }}>{n}</span>}
                />
              </RadarChart>
            </ResponsiveContainer>
          </ChartCard>

        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-600">
          IT &amp; total program counts sourced live from{' '}
          <span className="text-gray-500 font-medium">ontario_college_IT_programs_ONLY_DEDUP_COLLEGE_PROGRAM.csv</span>
          {' '}via the ML pipeline API · Fees, placement, salary &amp; ratings are representative estimates.
        </p>

      </div>
    </section>
  );
}
