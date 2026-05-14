export const config = {
  maxDuration: 300,
};

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const RAILWAY_URL = process.env.RAILWAY_PDF_URL || 'https://web-production-f8165.up.railway.app';

  try {
    const railwayRes = await fetch(`${RAILWAY_URL}/gerar-relatorio`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timestamp: new Date().toISOString() })
    });

    if (!railwayRes.ok) {
      const err = await railwayRes.text();
      return res.status(railwayRes.status).json({ error: err });
    }

    const pdf = await railwayRes.arrayBuffer();
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename="Relatorio_DOIC8000.pdf"');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.send(Buffer.from(pdf));

  } catch (err) {
    console.error('Erro:', err.message);
    res.status(500).json({ error: 'Erro no servico de PDF', details: err.message });
  }
};
