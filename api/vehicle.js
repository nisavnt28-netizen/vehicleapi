const XLSX = require('xlsx');
const path = require('path');
const fs = require('fs');

// ─── Config ───────────────────────────────────────────────────────────────────
const API_KEYS = (process.env.API_KEYS || 'test-key-123').split(',').map(k => k.trim());

// Common vehicle number column name variations
const VEHICLE_COL_HINTS = [
  'vehicle_number', 'vehicle number', 'vehiclenumber',
  'reg_no', 'reg no', 'regno', 'registration_no', 'registration no', 'registration',
  'number_plate', 'number plate', 'numberplate', 'plate', 'plate_no',
  'veh_no', 'veh no', 'vehicle_no', 'vehicle no',
  'rc_number', 'rc no', 'rc'
];

// ─── Load & cache xlsx ────────────────────────────────────────────────────────
let cachedData = null;
let detectedKeyCol = null;

function loadData() {
  if (cachedData) return { data: cachedData, keyCol: detectedKeyCol };

  const dbPath = path.join(process.cwd(), 'data', 'vehicles.xlsx');
  if (!fs.existsSync(dbPath)) throw new Error('Database file not found: data/vehicles.xlsx');

  const wb = XLSX.readFile(dbPath);
  const sheetName = wb.SheetNames[0];
  const sheet = wb.Sheets[sheetName];
  const rows = XLSX.utils.sheet_to_json(sheet, { defval: '' });

  if (!rows.length) throw new Error('Database is empty');

  // Auto-detect vehicle number column
  const cols = Object.keys(rows[0]);
  detectedKeyCol = cols.find(c =>
    VEHICLE_COL_HINTS.includes(c.toLowerCase().trim())
  ) || cols[0]; // fallback: first column

  cachedData = rows;
  return { data: cachedData, keyCol: detectedKeyCol };
}

// Normalize: uppercase, remove spaces/dashes/dots
function normalize(str) {
  return String(str).toUpperCase().replace(/[\s\-_.]/g, '');
}

// ─── Handler ──────────────────────────────────────────────────────────────────
module.exports = function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'x-api-key, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();

  // Only GET
  if (req.method !== 'GET') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  // ── Auth ──
  const apiKey =
    req.headers['x-api-key'] ||
    (req.headers['authorization'] || '').replace(/^Bearer\s+/i, '');

  if (!apiKey || !API_KEYS.includes(apiKey)) {
    return res.status(401).json({ success: false, error: 'Invalid or missing API key' });
  }

  // ── Param ──
  const vehicleNumber = (req.query.number || req.query.vehicle || '').trim();
  if (!vehicleNumber) {
    return res.status(400).json({
      success: false,
      error: 'Missing vehicle number. Use ?number=MH12AB1234'
    });
  }

  // ── Lookup ──
  try {
    const { data, keyCol } = loadData();
    const query = normalize(vehicleNumber);

    const result = data.find(row => normalize(row[keyCol]) === query);

    if (!result) {
      return res.status(404).json({
        success: false,
        error: 'Vehicle not found',
        queried: vehicleNumber.toUpperCase()
      });
    }

    // Clean empty fields
    const clean = Object.fromEntries(
      Object.entries(result).filter(([, v]) => v !== '' && v !== null && v !== undefined)
    );

    return res.status(200).json({
      success: true,
      vehicle: clean
    });

  } catch (err) {
    console.error('Vehicle API error:', err.message);
    return res.status(500).json({ success: false, error: err.message });
  }
};
