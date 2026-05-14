// ============================================================================
// api/gerar-relatorio.js — DOIC-8000
// Recebe o clique do usuario, chama o Railway (servico Python) e
// devolve o PDF pronto para download no navegador.
//
// CONFIGURACAO OBRIGATORIA NA VERCEL:
//   Settings → Environment Variables:
//   RAILWAY_PDF_URL = https://SEU-APP.railway.app
// ============================================================================

export const config = {
  maxDuration: 300,
};

module.exports = async function handler(req, res) {

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  var RAILWAY_URL = process.env.RAILWAY_PDF_URL;
  if (!RAILWAY_URL) {
    return res.status(500).json({
      error: 'RAILWAY_PDF_URL nao configurada.',
      instrucao: 'Configure RAILWAY_PDF_URL nas Environment Variables da Vercel com a URL do seu servico Railway.'
    });
  }

  try {
    console.log('DOIC-8000: chamando Railway PDF service...');

    var railwayRes = await fetch(RAILWAY_URL + '/gerar-relatorio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timestamp: new Date().toISOString() })
    });

    if (!railwayRes.ok) {
      var errText = await railwayRes.text();
      console.error('Erro Railway:', railwayRes.status, errText.substring(0, 200));
      return res.status(500).json({
        error: 'Erro no servico de PDF',
        details: errText
      });
    }

    // Railway devolveu o PDF — repassar direto para o navegador
    var pdfBuffer = await railwayRes.arrayBuffer();

    var data_str = new Date().toLocaleDateString('pt-BR')
      .split('/').reverse().join('').replace(/\//g, '');
    var filename = 'Relatorio_DOIC8000_' + data_str + '.pdf';

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename="' + filename + '"');
    res.setHeader('Content-Length', pdfBuffer.byteLength);

    return res.status(200).send(Buffer.from(pdfBuffer));

  } catch (error) {
    console.error('gerar-relatorio erro:', error.message);
    return res.status(500).json({ error: 'Erro ao gerar relatorio', details: error.message });
  }
};
