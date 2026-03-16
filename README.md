# MRP Repair Final (Odoo 16 Community)

Módulo de integração entre Manufatura (MRP) e Reparos (Repair) para Odoo 16 Community.

## Funcionalidades
- **Vínculo Bidirecional:** Linka Ordens de Produção (MO) diretamente a uma Ordem de Serviço (OS).
- **Rastreio Detalhado:** Campos para Produto Principal (NS), Componente, Operação e Centro de Trabalho dentro da MO.
- **Controle de Chão de Fábrica:** Status personalizado (Aguardando, Em Andamento, Concluído, Reprovado) independente do fluxo padrão do MRP.
- **Apontamento de Tempo:** Registro de hora de início e fim real da operação de reparo.
- **Dashboard de Progresso:** Barra de progresso automática na OS baseada na conclusão das MOs vinculadas.
- **Relatório Excel:** Botão para exportar um relatório técnico completo da OS com todas as MOs, tempos e observações.

## Instalação
1. Certifique-se de ter a biblioteca `xlsxwriter` instalada no servidor:
   ```bash
   pip3 install xlsxwriter
