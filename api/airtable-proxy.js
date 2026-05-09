// ============================================================================
// AIRTABLE PROXY - VERCEL SERVERLESS FUNCTION
// ATUALIZADO COM TABLE IDS CORRETOS
// ============================================================================

const AIRTABLE_TOKEN = process.env.AIRTABLE_TOKEN;
const BASE_ID = process.env.AIRTABLE_BASE_ID;

// Mapeamento de tabelas - ATUALIZADO COM IDS CORRETOS
const TABLE_IDS = {
    'ocorrencias': 'tblkUxc5lSchvoGMh',
    'briefing': 'tblzOF15Ptk5CzsjG',
    'radios': 'tblGBA4iHXoFk9nlO',
    'numeral_portarias': 'tbl4GmFUCRD7yyDWL',
    'info_eventos': 'tblf7CyxMnurOUCgO',
    'manutencoes': 'tblaJGFeemkpFV7uS',
    'checklist_central': 'tbl6vD27KyW7ry0d3',
    'levantamento': 'tblbL99fMoM7jFBxX',
    'solicitacao_imagem': 'tblFeaU4AFKMIrHH7',
    'autorizacoes_chaves': 'tblxFfl01a9IPhCyV',
    'controle_chaves': 'tblp7hSRRFqJqmGxn',
    'historico_chaves': 'tblakCAo2nt2m1qrd'
};

module.exports = async function handler(req, res) {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    // 🔍 DEBUG - RETORNAR AS VARIÁVEIS
    if (req.query.debug === 'true') {
        return res.status(200).json({
            debug: true,
            token_exists: !!AIRTABLE_TOKEN,
            token_length: AIRTABLE_TOKEN ? AIRTABLE_TOKEN.length : 0,
            token_start: AIRTABLE_TOKEN ? AIRTABLE_TOKEN.substring(0, 20) : 'NONE',
            base_id: BASE_ID || 'NONE',
            available_tables: Object.keys(TABLE_IDS)
        });
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { action, table, fields, recordId, maxRecords = 100 } = req.body;

        if (!table || !TABLE_IDS[table]) {
            return res.status(400).json({ 
                error: 'Invalid table name',
                available_tables: Object.keys(TABLE_IDS)
            });
        }

        const tableId = TABLE_IDS[table];
        const baseUrl = `https://api.airtable.com/v0/${BASE_ID}/${tableId}`;

        let response;

        switch (action) {
            case 'list':
                response = await fetch(`${baseUrl}?maxRecords=${maxRecords}`, {
                    headers: {
                        'Authorization': `Bearer ${AIRTABLE_TOKEN}`,
                        'Content-Type': 'application/json'
                    }
                });
                break;

            case 'create':
                response = await fetch(baseUrl, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${AIRTABLE_TOKEN}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ fields })
                });
                break;

            case 'update':
                if (!recordId) {
                    return res.status(400).json({ error: 'recordId required for update' });
                }
                response = await fetch(`${baseUrl}/${recordId}`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${AIRTABLE_TOKEN}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ fields })
                });
                break;

            case 'delete':
                if (!recordId) {
                    return res.status(400).json({ error: 'recordId required for delete' });
                }
                response = await fetch(`${baseUrl}/${recordId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${AIRTABLE_TOKEN}`,
                        'Content-Type': 'application/json'
                    }
                });
                break;

            default:
                return res.status(400).json({ error: 'Invalid action' });
        }

        const data = await response.json();

        if (!response.ok) {
            return res.status(response.status).json({ 
                error: data.error?.message || 'Airtable API error',
                details: data
            });
        }

        return res.status(200).json(data);

    } catch (error) {
        console.error('Proxy error:', error);
        return res.status(500).json({ 
            error: 'Internal server error',
            message: error.message 
        });
    }
}
