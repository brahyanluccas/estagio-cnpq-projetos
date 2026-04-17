import pandas as pd
import io
import os

# 1. BASE DE DADOS DA PERGUNTA 1 (O que mais gostou)
raw_p1 = """ID	Sentimento	Palavras-Chave	P	C	S
13	Elogio / Sugestão	Simples (P); Interativo (P); Deixar claro procedimento (S)	2	0	1
10	Elogio	Didático (P)	1	0	0
7	Elogio	Crescimento pessoal (P); Cuidados com dados (P)	2	0	0
11	Elogio	Videos curtos (P); Interativos (P)	2	0	0
9	Elogio	Didática (P)	1	0	0
19	Elogio	Chama atenção (P); Aspectos importantes (P)	2	0	0
12	Elogio	Tudo foi muito proveitoso (P)	1	0	0
3	-	-	0	0	0
14	Elogio	Organização (P); Forma clara (P)	2	0	0
15	Elogio	Tempo (P); Casos práticos (P); Clareza (P)	3	0	0
16	Elogio	Interessantes (P); Explicativos (P); Fácil entender (P)	3	0	0
20	Elogio	Distintas abordagens (P); Contribuiu para maturidade (P)	2	0	0
6	Elogio	Maneira cômica (P)	1	0	0
21	-	-	0	0	0
46	Elogio	Intuitivo (P); Dinâmico (P)	2	0	0
8	Elogio	Interface (P)	1	0	0
5	Elogio / Crítica / Sugestão	Interessantes (P); Repetitivos (C); Não sei contatos (C); Precisa saber contatos (S)	1	2	1
111	Elogio	Informações (P); Conscientização (P)	2	0	0
115	Elogio	Didatica (P)	1	0	0
22	Elogio	Lembretes (P); Novos conhecimentos (P)	2	0	0
29	Crítica	Carga massiva (C); Repetitivo (C); Chato (C)	0	3	0
26	Elogio / Crítica	Muito bom (P); Cronograma inadequado (C); Sobrecarga (C)	1	2	0
38	Elogio	Dinâmicas (P); Diversificadas (P)	2	0	0
28	Elogio	Aprendizagem (P)	1	0	0
31	Elogio	Importante (P); Conscientização (P)	2	0	0
24	Elogio	Objetiva (P)	1	0	0
43	Elogio	Curtos (P); Objetivos (P)	2	0	0
35	Elogio	Didática (P); Instrumentação (P)	2	0	0
42	Elogio	Conhecimentos (P)	1	0	0
27	Elogio	Didática (P); Conteúdo (P)	2	0	0
32	Elogio	Clareza (P); Prática (P)	2	0	0
25	Elogio	Quiz interativos (P); Histórias pertinentes (P)	2	0	0
37	Elogio / Crítica / Sugestão	Conteúdo (P); Planejamento incomodou (C); Uma por semana (S)	1	1	1
41	Elogio	Facilidade de acesso (P)	1	0	0
36	Sugestão	Indicar e-mail abuse (S)	0	0	1
44	Crítica	Faltou identidade (C)	0	1	0
45	Elogio	Diversidade (P)	1	0	0
33	Elogio	Dinâmicas (P); Diversificadas (P)	2	0	0
51	Elogio	Didática (P)	1	0	0
48	Elogio	Úteis (P)	1	0	0
58	Crítica	Não gostei (C); Pouco intuitiva (C); Defasados (C)	0	3	0
62	Sugestão / Crítica	Muitos cursos juntos (C); Não enviar juntos (S)	0	1	1
59	Elogio	Fácil compreensão (P); Cobriram bem (P)	2	0	0
54	Elogio	Conteúdo (P)	1	0	0
67	Elogio	Didáticos (P)	1	0	0
55	Elogio	Proposta de educar (P)	1	0	0
64	-	-	0	0	0
56	Elogio	Mensagens de atenção (P)	1	0	0
63	Crítica	Não gostei (C)	0	1	0
65	-	-	0	0	0
60	Elogio	Exercícios (P)	1	0	0
72	Elogio	Explicações claras (P); Charadas (P)	2	0	0
109	Elogio	Aprender proteger (P); Identificar perigos (P)	2	0	0
116	-	-	0	0	0
71	Crítica	Não gostou (C); Autoritarismo (C); Ameaça (C); Constrangedor (C)	0	4	0
112	Elogio	Aplico o que aprendi (P)	1	0	0
110	Elogio / Sugestão	Didático (P); Fácil compreensão (P); Canal específico (S)	2	0	1
76	-	-	0	0	0
74	Elogio	Dinâmica (P); Exercícios (P); Comunicação (P)	3	0	0
118	Elogio	Prática (P); Interativa (P); Refletir rotina (P)	3	0	0
119	Crítica / Sugestão	Faltou informação (C); Informação mandatória (S)	0	1	1
114	Elogio	Interatividade (P)	1	0	0
75	Elogio	Novidades (P); Reforço LGPD (P)	2	0	0
78	Elogio	Alerta (P); Criação de senhas (P)	2	0	0
117	Elogio	Forma abordada (P)	1	0	0
121	Elogio	Gostei (P)	1	0	0
77	Elogio	Diversas situações (P)	1	0	0
79	Elogio	Informação útil (P)	1	0	0
83	Elogio	Quiz (P); Games (P); Interessante (P)	3	0	0
90	Elogio	Vídeos curtos (P); Explicação técnica (P)	2	0	0
99	Elogio	Quiz interativo (P); Aprendizado (P)	2	0	0
86	Elogio	Gostei (P); Conteúdo (P)	2	0	0
82	Elogio	Prático (P); Didático (P)	2	0	0
91	Elogio	De tudo (P)	1	0	0
93	Elogio	Tudo (P); Aprendi coisas (P)	2	0	0
80	-	-	0	0	0
84	Elogio	Objetividade (P)	1	0	0
81	Elogio	Parabéns (P)	1	0	0
88	Elogio	Dicas (P)	1	0	0
85	Elogio	Joguinhos (P); Criativos (P)	2	0	0
94	Elogio	Dinâmicas (P); Testes (P)	2	0	0
106	Crítica	Repetitivos (C)	0	1	0
98	Elogio	Forma do quiz (P)	1	0	0
102	Elogio	Tudo (P); Animações (P)	2	0	0
107	Elogio	Orientação (P)	1	0	0
108	Elogio	Fatos (P)	1	0	0
120	Crítica	Vergonha (C); Idiota (C); Ridículo (C)	0	3	0"""

# 2. BASE DE DADOS DA PERGUNTA 2 (O que melhorar)
raw_p2 = """ID	Sentimento	Palavras-Chave	P	C	S
13	-	-	0	0	0
10	Crítica / Sugestão	Vídeos longos (C); difícil pararmos (C); não tão longos (S)	0	2	1
7	Sugestão	Novos cursos (S); orientar (S)	0	0	2
11	Sugestão	Aprofundamento (S)	0	0	1
9	Sugestão	Gabarito (S)	0	0	1
19	Crítica / Sugestão	Repetições (C); Conjugar atividades (S)	0	1	1
12	Sugestão	Novas atualizações (S)	0	0	1
18	Crítica / Sugestão	Repetitivo (C); Infantilizadas (C); Prefiro texto (S)	0	2	1
3	-	-	0	0	0
14	Elogio / Sugestão	Bem conduzido (P); Aprimorar tempo (S)	1	0	1
17	Crítica	Repetitivos (C)	0	1	0
15	-	-	0	0	0
20	Sugestão	Incentivos (S)	0	0	1
4	Crítica / Sugestão	Repetitivo (C); Mais enxuto (S)	0	1	1
6	Sugestão	Vídeos mais curtos (S)	0	0	1
21	Crítica / Sugestão	Demanda grande (C); Diminuir tarefas (S)	0	1	1
46	Elogio	Manter (P); Ótimo (P)	2	0	0
8	Sugestão	Aumento de prazos (S)	0	0	1
5	Crítica / Sugestão	Repetitivo (C); Mais aplicado (S); Mencionar setores (S)	0	1	2
115	Sugestão	Menos conteúdo (S)	0	0	1
22	Crítica / Sugestão	Tempo ínfimo (C); Encurtem módulos (S); Sucinta (S)	0	1	2
29	Crítica / Sugestão	Muitos exercícios (C); Semestral (S)	0	1	1
26	Crítica / Sugestão	Falhas nos sistemas (C); Ajustar cronograma (S)	0	1	1
38	Sugestão	Baixar certificados de uma vez (S)	0	0	1
28	Sugestão	Mais conteúdo (S)	0	0	1
31	Elogio	Ótimo (P)	1	0	0
24	Sugestão	Divulgação (S)	0	0	1
43	Crítica	Perguntas confusas (C)	0	1	0
35	Sugestão	Certificado único (S)	0	0	1
42	Crítica / Sugestão	Precisa melhorar (C); E-mails claros e objetivos (S)	0	1	1
27	Sugestão	Exemplos práticos (S)	0	0	1
32	Sugestão	Aprofundamento (S); Realidade da instituição (S)	0	0	2
25	Sugestão	Menos conteudista (S)	0	0	1
37	Sugestão	Planejamento de divulgação (S)	0	0	1
41	Crítica	Infantil (C); Rasa (C)	0	2	0
36	Sugestão	Adequação à realidade (S)	0	0	1
44	Sugestão	Transparência (S); Fóruns (S)	0	0	2
40	Sugestão	Quiz e outros (S)	0	0	1
45	Sugestão	Maior engajamento (S)	0	0	1
33	Sugestão	Download de uma vez (S)	0	0	1
51	Sugestão	Informações claras (S)	0	0	1
48	Sugestão	Entender nível de conhecimento (S)	0	0	1
58	Crítica / Sugestão	Gestão não permite (C); Cursos customizados (S)	0	1	1
59	Sugestão	Pílulas de Segurança (S); Conteúdo curto (S)	0	0	2
54	Sugestão	Exemplos práticos (S)	0	0	1
67	Crítica / Sugestão	Repetitivos (C); Associar realidade (S)	0	1	1
55	Crítica / Sugestão	Feito por obrigação (C); Organizado (S); Sanção (S)	0	1	2
64	-	-	0	0	0
56	Crítica	Layouts ruins (C); Exercícios ruins (C)	0	2	0
63	Crítica / Sugestão	Forçar servidores (C); Avaliar necessidade (S)	0	1	1
65	Sugestão	Mostrar resultado (S)	0	0	1
60	Sugestão	Material atualizado (S)	0	0	1
72	Elogio	Manter padrão (P)	1	0	0
109	Elogio	Seguir mesma linha (P)	1	0	0
113	Sugestão	Comunicação (S); Divulgação (S)	0	0	2
116	-	-	0	0	0
71	Crítica / Sugestão	Não ter próxima (C); Assédio institucional (C); Transparência (S)	0	2	1
112	-	-	0	0	0
110	Sugestão	Canal específico (S); Intranet (S)	0	0	2
76	-	-	0	0	0
74	Sugestão	Aprofundamento (S); Casos recentes (S)	0	0	2
118	Sugestão	Atividades práticas (S); Materiais de apoio (S)	0	0	2
114	-	-	0	0	0
75	Sugestão	Módulo IA (S)	0	0	1
78	-	-	0	0	0
117	-	-	0	0	0
121	Elogio	Gostei (P)	1	0	0
77	Sugestão	Maior divulgação (S)	0	0	1
79	Sugestão	Apresentação institucional (S)	0	0	1
83	-	-	0	0	0
90	Sugestão	Medir conhecimento (S); Escala de nível (S)	0	0	2
99	Elogio	Adequado (P)	1	0	0
86	Elogio	Perfeito (P)	1	0	0
82	-	-	0	0	0
91	Elogio	De acordo (P)	1	0	0
93	Sugestão	Tempo de entrega (S)	0	0	1
80	Elogio	Adequada (P); Intuitivos (P)	2	0	0
84	-	-	0	0	0
81	Elogio	Parabéns (P)	1	0	0
88	Sugestão	Prazo maior (S)	0	0	1
94	-	-	0	0	0
106	Sugestão	Menos quiz (S)	0	0	1
98	Elogio	Ta bom (P)	1	0	0
105	Crítica	Não genérico (C); Fraca adaptação (C)	0	2	0
102	Elogio	Edições ideais (P)	1	0	0
107	-	-	0	0	0
108	Elogio	Gostei (P)	1	0	0
120	Crítica	Não ocorrer (C); Perca de tempo (C)	0	2	0"""

# 3. BASE DE DADOS DA PERGUNTA 3 (Comentários adicionais)
raw_p3 = """ID	Sentimento	Palavras-Chave	P	C	S
13	Crítica / Sugestão	Condução confusa (C); Deve ser mais claro (S)	0	1	1
7	Elogio	Agradecimento (P); Desejo de aprender (P)	2	0	0
11	Sugestão	Temas aprofundados (S); CIA (S); Nuvem (S)	0	0	3
9	-	-	0	0	0
12	Elogio	Agradecimentos (P)	1	0	0
3	-	-	0	0	0
14	-	-	0	0	0
15	-	-	0	0	0
20	Sugestão	Casos práticos (S); Exemplos verídicos (S)	0	0	2
21	-	-	0	0	0
8	-	-	0	0	0
115	-	-	0	0	0
22	Elogio	Parabéns (P); Ganhamos com a iniciativa (P)	2	0	0
38	Elogio	Papel essencial (P); Promover ações (P)	2	0	0
28	Elogio	Muito bom (P); Aprender (P)	2	0	0
24	Crítica / Sugestão	Chefias não empenhadas (C); Campanha visual (S)	0	1	1
35	Elogio	Grato (P)	1	0	0
32	Elogio	Parabéns (P); Relevante (P)	2	0	0
25	-	-	0	0	0
41	-	-	0	0	0
36	Sugestão	Atividades práticas (S)	0	0	1
55	-	-	0	0	0
63	Crítica	Fomos forçados (C); Ameaça de perder PGD (C)	0	2	0
65	-	-	0	0	0
61	Elogio	Dinâmico (P); Proveitoso (P); Apoio/Disponibilidade (P)	3	0	0
72	Elogio	Enriquecer conhecimento (P); Vídeos relevantes (P)	2	0	0
71	Crítica	Autoritarismo (C); Opressão (C); Constrangedor (C); Não se repita (C)	0	4	0
112	Crítica	Dificuldade nas leis (C)	0	1	0
74	-	-	0	0	0
118	Elogio / Sugestão	Enriquecedor (P); Mudanças positivas (P); Ser ampliada (S)	2	0	1
114	-	-	0	0	0
78	Sugestão	Reuniões presenciais (S); Mostrar pessoalmente (S)	0	0	2
121	Elogio / Crítica	Ações válidas (P); Sem tempo (C)	1	1	0
79	Crítica / Sugestão	Subaproveitadas (C); Dar de ombros (C); Modelagem coletiva (S)	0	2	1
99	Elogio	Ajudou a evitar golpe (P)	1	0	0
93	Elogio	Espero que continue (P)	1	0	0
84	Elogio	Conteúdo adequado (P); Carga horária adequada (P)	2	0	0
81	Elogio	Parabéns (P)	1	0	0
88	Elogio	Gostei muito (P)	1	0	0
98	Elogio	Parabéns (P)	1	0	0
105	Crítica	Soluções não disponíveis (C)	0	1	0
102	Elogio	Muito bom (P); Atualizada (P)	2	0	0
120	Crítica	Vergonha (C); Incompetência TI (C); Ridículo (C)	0	3	0"""

# CONFIGURAÇÕES DE ARQUIVOS
ARQUIVO_ENTRADA = "Dados Pesquisa por questões (1).xls"
ARQUIVO_SAIDA = "Relatorio_Analitico_Integridade_Total.xlsx"
LEGENDA = "LEGENDA: (P) Positivo | (C) Crítica | (S) Sugestão"

INFO_ABAS = {
    "Pergunta 1": {"pergunta": "9. O que você mais gostou no programa?", "data": raw_p1},
    "Pergunta 2": {"pergunta": "10. O que pode ser melhorado para as próximas edições?", "data": raw_p2},
    "Pergunta 3": {"pergunta": "11. Comentários adicionais (opcional)", "data": raw_p3}
}

def processar():
    print("🚀 Iniciando consolidação com integridade total dos dados...")
    
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"❌ Erro: O arquivo '{ARQUIVO_ENTRADA}' não foi encontrado.")
        return

    writer = pd.ExcelWriter(ARQUIVO_SAIDA, engine='openpyxl')
    resumo_geral = []

    for nome_aba, info in INFO_ABAS.items():
        print(f"📦 Processando aba: {nome_aba}")
        
        # 1. Carrega o Original (Para pegar a frase COMPLETA)
        df_original = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=nome_aba, header=3)
        df_original = df_original.dropna(subset=['Resposta'])
        
        # 2. Carrega a Análise da IA
        df_analise = pd.read_csv(io.StringIO(info['data']), sep='\t')
        
        # 3. Faz o MERGE (Une os dois pelo ID)
        # O 'how=left' garante que mantemos as frases originais e apenas 'grudamos' as notas
        df_final = pd.merge(df_original, df_analise[['ID', 'Sentimento', 'Palavras-Chave', 'P', 'C', 'S']], on='ID', how='left')

        # Escreve Legenda e Pergunta no topo
        pd.DataFrame([LEGENDA]).to_excel(writer, sheet_name=nome_aba, startrow=0, index=False, header=False)
        pd.DataFrame([f"PERGUNTA: {info['pergunta']}"]).to_excel(writer, sheet_name=nome_aba, startrow=1, index=False, header=False)
        
        # Salva a tabela principal
        df_final.to_excel(writer, sheet_name=nome_aba, startrow=3, index=False)

        # 4. Cálculo do Resumo
        tp, tc, ts = df_final['P'].sum(), df_final['C'].sum(), df_final['S'].sum()
        total = tp + tc + ts
        resumo_geral.append({
            "Pergunta": nome_aba,
            "Total Menções": total,
            "Positivos (P)": tp,
            "Críticas (C)": tc,
            "Sugestões (S)": ts,
            "Aproveitamento": f"{(tp/total*100):.1f}%" if total > 0 else "0%"
        })

    # Cria aba de Resumo Executivo
    pd.DataFrame(resumo_geral).to_excel(writer, sheet_name="Resumo Executivo", index=False)
    
    writer.close()
    print(f"\n✨ CONCLUÍDO! O arquivo '{ARQUIVO_SAIDA}' foi gerado com os TEXTOS ORIGINAIS.")

if __name__ == "__main__":
    processar()