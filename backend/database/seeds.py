from .schema import criar_banco
from typing import List, Dict, Any

DADOS_INICIAIS: Dict[str, List[Any]] = {
    'categorias': [
        ('Medicina', 'Termos médicos e de saúde'),
        ('Direito', 'Termos jurídicos e legais'),
        ('Literatura', 'Termos literários e poéticos')
    ],
    'palavras': [
        ('Macroglossia', 'Aumento anormal da língua', 1, 4),
        ('Habeas Corpus', 'Remédio constitucional', 2, 3),
        ('Bacharelesco', 'Que mostra erudição afetada', 3, 2)
    ],
    'frases': [
        ('O diagnóstico de macroglossia foi confirmado pelo exame físico', 1),
        ('O advogado impetrou um habeas corpus em favor do cliente', 2),
        ('Seu discurso bacharelesco mais confundia do que explicava', 3)
    ],
    'variacoes': [
        (1, 'aumento da língua'),
        (1, 'língua grande'),
        (1, 'crescimento anormal da língua'),
        (2, 'garantia de liberdade'),
        (2, 'direito de ir e vir'),
        (3, 'linguagem pretensiosa')
    ]
}

def popular_banco(conn):
    """Popula o banco com dados iniciais incluindo variações"""
    try:
        cursor = conn.cursor()
        
        # Inserção em lote otimizada
        cursor.executemany(
            "INSERT INTO categorias (nome, descricao) VALUES (?, ?)",
            DADOS_INICIAIS['categorias']
        )
        
        cursor.executemany(
            """INSERT INTO palavras 
            (palavra, definicao, categoria_id, dificuldade) 
            VALUES (?, ?, ?, ?)""",
            DADOS_INICIAIS['palavras']
        )
        
        cursor.executemany(
            "INSERT INTO frases (frase, palavra_id) VALUES (?, ?)",
            DADOS_INICIAIS['frases']
        )
        
        cursor.executemany(
            "INSERT INTO variacoes_aceitas (palavra_id, variacao) VALUES (?, ?)",
            DADOS_INICIAIS['variacoes']
        )
        
        conn.commit()
        print("✅ Dados iniciais inseridos com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {e}")
        conn.rollback()
        return False