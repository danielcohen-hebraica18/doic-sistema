// ============================================================================
// api/google-search.js — DOIC-8000
// NewsAPI não funciona em produção (plano free bloqueado fora de localhost).
// Este endpoint agora retorna lista vazia de forma segura, sem quebrar o fluxo.
// A busca real é feita pelo Claude via ferramenta web_search nativa (claude-proxy).
// ============================================================================

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');

  if (req.method === 'OPTIONS') return res.status(200).end();

  // Retorna OK com lista vazia — o frontend trata graciosamente
  return res.status(200).json({ query: (req.body || {}).query || '', results: [] });
};
