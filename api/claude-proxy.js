// ============================================================================
// api/claude-proxy.js — DOIC-8000
// Proxy seguro para a Anthropic API
//
// CONFIGURAÇÃO OBRIGATÓRIA NA VERCEL:
//   Settings → Environment Variables → ANTHROPIC_API_KEY = sk-ant-...
//
// NÃO coloque a chave aqui. Ela deve viver APENAS como variável de ambiente.
// ============================================================================

module.exports = async function handler(req, res) {

  // ── CORS ──────────────────────────────────────────────────────────────────
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed', expected: 'POST' });
  }

  // ── Chave vem SEMPRE da variável de ambiente ───────────────────────────────
  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  if (!ANTHROPIC_API_KEY) {
    console.error('ANTHROPIC_API_KEY nao configurada nas env vars da Vercel!');
    return res.status(500).json({
      error: 'Chave de API nao configurada no servidor.',
      instrucao: 'Configure ANTHROPIC_API_KEY nas Environment Variables da Vercel.'
    });
  }

  try {
    const body = req.body;

    if (!body || !body.messages || !body.model) {
      return res.status(400).json({ error: 'Campos obrigatorios: model, messages' });
    }

    console.log('claude-proxy -> Anthropic | modelo:', body.model,
      '| tools:', body.tools ? body.tools.map(function(t){ return t.name; }).join(',') : 'nenhuma');

    // ── Payload para a Anthropic ───────────────────────────────────────────
    var payload = {
      model:      body.model      || 'claude-sonnet-4-20250514',
      max_tokens: body.max_tokens || 8192,
      messages:   body.messages,
    };
    if (body.system)                    payload.system      = body.system;
    if (body.temperature !== undefined) payload.temperature = body.temperature;
    if (body.tools)                     payload.tools       = body.tools;
    if (body.tool_choice)               payload.tool_choice = body.tool_choice;

    // ── Chamada à Anthropic ────────────────────────────────────────────────
    var anthropicRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type':      'application/json',
        'x-api-key':         ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'anthropic-beta':    'web-search-2025-03-05',
      },
      body: JSON.stringify(payload),
    });

    var responseText = await anthropicRes.text();

    if (!anthropicRes.ok) {
      console.error('Anthropic API erro:', anthropicRes.status, responseText.substring(0, 300));
      return res.status(anthropicRes.status).json({
        error: 'Anthropic API erro ' + anthropicRes.status,
        details: JSON.parse(responseText)
      });
    }

    var data = JSON.parse(responseText);
    console.log('claude-proxy OK | stop_reason:', data.stop_reason,
      '| blocos:', data.content ? data.content.length : 0);

    return res.status(200).json(data);

  } catch (error) {
    console.error('claude-proxy erro interno:', error.message);
    return res.status(500).json({ error: 'Erro interno no proxy', details: error.message });
  }
};
