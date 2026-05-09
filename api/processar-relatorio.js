// ============================================================================
// api/processar-relatorio.js — DOIC-8000
// Recebe a resposta bruta do Claude (search_results) e a reenvia ao Claude
// para estruturar os dados em JSON seguindo o protocolo DOIC-8000.
// ============================================================================

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  var ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  if (!ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY nao configurada' });
  }

  try {
    var body = req.body;
    var search_results = body.search_results;

    if (!search_results) {
      return res.status(400).json({ error: 'search_results obrigatorio' });
    }

    // Extrair texto da resposta do Claude (pode vir como array de content blocks)
    var textoColetado = '';
    if (Array.isArray(search_results)) {
      search_results.forEach(function(block) {
        if (block.type === 'text' && block.text) {
          textoColetado += block.text + '\n';
        }
      });
    } else if (typeof search_results === 'string') {
      textoColetado = search_results;
    }

    if (!textoColetado.trim()) {
      textoColetado = 'Sem dados coletados na busca.';
    }

    var agora = new Date();
    var dataEmissao = agora.toLocaleDateString('pt-BR');
    var corteColeta = agora.toLocaleString('pt-BR', {
      day: 'numeric', month: 'long', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    }) + ' (horario de Brasilia)';

    // Prompt para estruturar os dados em JSON DOIC-8000
    var promptEstruturacao =
      'Voce e um Analista de Inteligencia Senior do Protocolo DOIC-8000.\n\n' +
      'Abaixo estao os dados brutos coletados pela busca web sobre terrorismo, ' +
      'antissemitismo e ameacas contra Israel e a comunidade judaica.\n\n' +
      'DATA DE EMISSAO: ' + dataEmissao + '\n' +
      'CORTE DA COLETA: ' + corteColeta + '\n\n' +
      '===== DADOS COLETADOS =====\n' +
      textoColetado.substring(0, 12000) +
      '\n===== FIM DOS DADOS =====\n\n' +
      'INSTRUCAO CRITICA: Analise os dados acima e retorne APENAS um objeto JSON valido ' +
      '(sem markdown, sem texto antes ou depois, sem ```json) seguindo EXATAMENTE esta estrutura:\n\n' +
      '{\n' +
      '  "protocolo": "DOIC-8000",\n' +
      '  "data_emissao": "' + dataEmissao + '",\n' +
      '  "corte_coleta": "' + corteColeta + '",\n' +
      '  "classificacao": "USO INTERNO - RESTRITO",\n' +
      '  "nivel_ameaca_global": "ALTO ou MODERADO-ALTO ou MODERADO (escolha com base nos dados)",\n' +
      '  "nivel_alerta_hebraica": "MODERADO-ELEVADO ou ELEVADO ou MODERADO (escolha com base nos dados)",\n' +
      '  "resumo_executivo": {\n' +
      '    "periodo": "Ultimas 24-72 horas",\n' +
      '    "contexto_geopolitico": "resumo do cenario geopolitico Israel/Ira/Oriente Medio (2-4 frases)",\n' +
      '    "padrao_europeu": "resumo de ataques antisemitas na Europa e UK (2-4 frases)",\n' +
      '    "reflexo_brasil": "avaliacao do reflexo no Brasil e na Hebraica SP (2-4 frases)"\n' +
      '  },\n' +
      '  "tabela_ocorrencias": [\n' +
      '    {\n' +
      '      "data": "DD/MM/AAAA",\n' +
      '      "local": "cidade/pais",\n' +
      '      "classificacao": "tipo do incidente",\n' +
      '      "resumo": "descricao em 1 frase",\n' +
      '      "gravidade": "CRITICO ou ALTO ou MEDIO ou BAIXO",\n' +
      '      "validacao": "A1 ou A2 ou B2 etc + descricao",\n' +
      '      "fonte_principal": "nome da fonte"\n' +
      '    }\n' +
      '  ],\n' +
      '  "sinais_emergentes": [\n' +
      '    {\n' +
      '      "numero": 1,\n' +
      '      "titulo": "titulo do sinal",\n' +
      '      "descricao": "descricao detalhada do sinal emergente (3-5 frases)",\n' +
      '      "fonte": "fontes utilizadas",\n' +
      '      "situacao_analitica": "Confirmado ou Parcialmente Corroborado ou Hipotese Analitica",\n' +
      '      "recomendacao": "acao recomendada"\n' +
      '    }\n' +
      '  ],\n' +
      '  "grade_riscos": [\n' +
      '    {\n' +
      '      "risco": "nome do risco",\n' +
      '      "probabilidade": 5,\n' +
      '      "impacto": 5,\n' +
      '      "score": 25,\n' +
      '      "classificacao": "CRITICO ou ALTO ou RELEVANTE ou MODERADO",\n' +
      '      "justificativa": "justificativa em 1 frase",\n' +
      '      "mitigacao": "acao de mitigacao"\n' +
      '    }\n' +
      '  ],\n' +
      '  "avaliacao_impacto": {\n' +
      '    "nivel_alerta_recomendado": "MODERADO-ELEVADO",\n' +
      '    "justificativa_nivel": "justificativa em 2-3 frases",\n' +
      '    "risco_fisico": "avaliacao do risco fisico para a Hebraica",\n' +
      '    "risco_digital": "avaliacao do risco digital",\n' +
      '    "risco_reputacional": "avaliacao do risco reputacional",\n' +
      '    "criterios_elevacao": ["criterio 1", "criterio 2", "criterio 3"]\n' +
      '  },\n' +
      '  "recomendacoes": {\n' +
      '    "imediatas_24h": [\n' +
      '      {"acao": "descricao da acao", "prioridade": "CRITICA ou ALTA ou MEDIA"}\n' +
      '    ],\n' +
      '    "curto_prazo_3_15_dias": [\n' +
      '      {"acao": "descricao da acao", "prioridade": "ALTA ou MEDIA"}\n' +
      '    ],\n' +
      '    "medio_prazo_15_30_dias": [\n' +
      '      {"acao": "descricao da acao", "prioridade": "ALTA ou MEDIA"}\n' +
      '    ]\n' +
      '  },\n' +
      '  "dashboard": {\n' +
      '    "nivel_geral_ameaca": "ALTO",\n' +
      '    "nivel_alerta_hebraica": "MODERADO-ELEVADO",\n' +
      '    "total_ocorrencias": {"ultimas_24h": 0, "ultimas_72h": 0},\n' +
      '    "top_3_vetores": [\n' +
      '      {"vetor": "nome", "justificativa": "motivo"}\n' +
      '    ],\n' +
      '    "paises_sensiveis": ["Israel", "UK", "Iran"],\n' +
      '    "semaforo": {"cor": "VERMELHO", "nivel": "CRITICO", "texto": "descricao"},\n' +
      '    "recomendacoes_prioritarias": ["acao 1", "acao 2", "acao 3"]\n' +
      '  },\n' +
      '  "relatorio_consolidado": {\n' +
      '    "sintese_ciclo": "sintese em 2-3 frases",\n' +
      '    "contexto_estrategico": "contexto estrategico em 2-3 frases",\n' +
      '    "risco_agregado": "ALTO ou MODERADO-ALTO",\n' +
      '    "implicacoes_hebraica": "implicacoes para a Hebraica SP em 2-3 frases",\n' +
      '    "limitacoes_analiticas": ["limitacao 1", "limitacao 2"]\n' +
      '  }\n' +
      '}\n\n' +
      'REGRAS:\n' +
      '1. Use APENAS dados dos textos coletados acima\n' +
      '2. Inclua MINIMO 5 ocorrencias na tabela_ocorrencias\n' +
      '3. Inclua MINIMO 2 sinais_emergentes\n' +
      '4. Inclua MINIMO 4 riscos na grade_riscos\n' +
      '5. Inclua MINIMO 3 recomendacoes imediatas\n' +
      '6. Retorne SOMENTE o JSON, sem nenhum texto adicional\n' +
      '7. O JSON deve ser valido e sem caracteres especiais problemáticos';

    console.log('processar-relatorio: chamando Claude para estruturar dados...');

    var estruturarRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type':      'application/json',
        'x-api-key':         ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'anthropic-beta':    'web-search-2025-03-05',
      },
      body: JSON.stringify({
        model:      'claude-sonnet-4-20250514',
        max_tokens: 8000,
        temperature: 0.1,
        system: promptEstruturacao,
        messages: [{
          role: 'user',
          content: 'Estruture os dados coletados no formato JSON DOIC-8000 conforme instrucoes.'
        }]
      })
    });

    var estruturarText = await estruturarRes.text();

    if (!estruturarRes.ok) {
      console.error('Erro ao estruturar:', estruturarRes.status, estruturarText.substring(0, 200));
      return res.status(500).json({ error: 'Erro ao estruturar dados', details: estruturarText });
    }

    var estruturarData = JSON.parse(estruturarText);
    var jsonText = '';

    if (estruturarData.content && Array.isArray(estruturarData.content)) {
      estruturarData.content.forEach(function(block) {
        if (block.type === 'text') jsonText += block.text;
      });
    }

    // Limpar markdown se vier com backticks
    jsonText = jsonText.trim()
      .replace(/^```json\s*/i, '')
      .replace(/^```\s*/i, '')
      .replace(/\s*```$/i, '')
      .trim();

    var dadosEstruturados;
    try {
      dadosEstruturados = JSON.parse(jsonText);
    } catch (parseErr) {
      console.error('Erro ao fazer parse do JSON:', parseErr.message);
      console.error('Texto recebido:', jsonText.substring(0, 500));
      // Fallback: retorna estrutura mínima com o texto bruto
      dadosEstruturados = {
        protocolo: 'DOIC-8000',
        data_emissao: dataEmissao,
        corte_coleta: corteColeta,
        classificacao: 'USO INTERNO - RESTRITO',
        nivel_ameaca_global: 'ALTO',
        nivel_alerta_hebraica: 'MODERADO-ELEVADO',
        resumo_executivo: {
          periodo: 'Ultimas 24-72 horas',
          contexto_geopolitico: textoColetado.substring(0, 500),
          padrao_europeu: 'Ver dados coletados.',
          reflexo_brasil: 'Monitoramento recomendado.'
        },
        tabela_ocorrencias: [],
        sinais_emergentes: [],
        grade_riscos: [],
        avaliacao_impacto: { nivel_alerta_recomendado: 'MODERADO-ELEVADO', justificativa_nivel: 'Ver relatorio.' },
        recomendacoes: { imediatas_24h: [], curto_prazo_3_15_dias: [], medio_prazo_15_30_dias: [] },
        dashboard: { nivel_geral_ameaca: 'ALTO', nivel_alerta_hebraica: 'MODERADO-ELEVADO', top_3_vetores: [], paises_sensiveis: [], semaforo: { cor: 'VERMELHO', nivel: 'ALTO', texto: 'Ver relatorio.' }, recomendacoes_prioritarias: [] },
        relatorio_consolidado: { sintese_ciclo: 'Ver dados coletados.', risco_agregado: 'ALTO', implicacoes_hebraica: 'Monitoramento recomendado.', limitacoes_analiticas: ['Estruturacao automatica falhou - usar dados brutos'] }
      };
    }

    console.log('processar-relatorio OK | ocorrencias:', (dadosEstruturados.tabela_ocorrencias || []).length);

    return res.status(200).json({ success: true, dados: dadosEstruturados });

  } catch (error) {
    console.error('processar-relatorio erro:', error.message);
    return res.status(500).json({ error: 'Erro ao processar relatorio', details: error.message });
  }
};
