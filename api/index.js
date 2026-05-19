module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.status(200).json({
    status: 'ok',
    name: 'Vehicle Info API',
    version: '1.0.0',
    endpoints: {
      lookup: 'GET /api/vehicle?number=MH12AB1234',
      headers: { 'x-api-key': 'your-api-key' }
    }
  });
};
