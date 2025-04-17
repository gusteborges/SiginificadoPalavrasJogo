from typing import List
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import sqlite3
from backend.config import DB_PATH

class GeradorFrases:
    def __init__(self):
        """Inicializa o gerador de frases com o Mistral AI"""
        # Carrega o arquivo .env do diretório raiz
        load_dotenv(find_dotenv())
        
        # Obtém a chave API
        api_key = os.environ.get('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError(
                "MISTRAL_API_KEY não encontrada. Verifique se:\n"
                "1. O arquivo .env existe no diretório raiz\n"
                "2. A variável MISTRAL_API_KEY está definida corretamente no arquivo\n"
                "3. O arquivo .env está no formato correto (sem espaços extras)"
            )
            
        try:
            # Configura o cliente OpenAI com o endpoint do Mistral
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.mistral.ai/v1"
            )
            
            # Testa a conexão
            response = self.client.chat.completions.create(
                model="mistral-tiny",
                messages=[{"role": "user", "content": "Teste de conexão"}],
                max_tokens=10
            )
            if not response.choices[0].message.content:
                raise ValueError("Não foi possível conectar ao modelo Mistral")
            print("✅ Modelo Mistral inicializado com sucesso")
            
        except Exception as e:
            print(f"⚠️ Erro ao inicializar Mistral: {str(e)}")
            self.client = None
            
    def gerar_frase_padrao(self, palavra: str, indice: int = 0) -> str:
        """Gera uma frase padrão quando o modelo não está disponível"""
        frases_padrao = [
            f"Esta é uma frase de exemplo usando a palavra '{palavra}'.",
            f"Aqui está outro exemplo com '{palavra}'.",
            f"E esta é a terceira frase com '{palavra}'."
        ]
        return frases_padrao[indice % len(frases_padrao)]
        
    def gerar_frases(self, palavra: str, definicao: str, categoria: str, palavra_id: int = None) -> List[str]:
        """
        Gera frases de exemplo usando a palavra no contexto correto.
        
        Args:
            palavra: A palavra para gerar frases
            definicao: A definição da palavra
            categoria: A categoria da palavra
            palavra_id: ID da palavra no banco de dados (opcional)
            
        Returns:
            Lista com 3 frases de exemplo
        """
        # Se o modelo não está disponível, retorna frases padrão
        if not self.client:
            return [self.gerar_frase_padrao(palavra, i) for i in range(3)]

        # Se temos o ID da palavra, primeiro verificamos se já existem frases no banco
        if palavra_id:
            try:
                # Busca frases existentes
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Busca frases existentes
                cursor.execute("""
                    SELECT frase FROM frases 
                    WHERE palavra_id = ? 
                    AND frase NOT LIKE 'Esta é uma frase de exemplo%'
                    AND frase NOT LIKE 'Aqui está outro exemplo%'
                    ORDER BY rowid
                    LIMIT 3
                """, (palavra_id,))
                
                frases_existentes = [row[0] for row in cursor.fetchall()]
                
                # Se já temos 3 frases, retornamos elas
                if len(frases_existentes) >= 3:
                    conn.close()
                    return frases_existentes[:3]
                    
                conn.close()
                
            except Exception as e:
                print(f"⚠️ Erro ao buscar frases existentes: {str(e)}")

        prompt = f"""
        Gere 3 frases em português que usem a palavra "{palavra}" em contextos naturais do dia a dia.
        
        Informações sobre a palavra:
        - Definição: {definicao}
        - Categoria: {categoria}
        
        Regras para as frases:
        1. Use a palavra de forma sutil e natural, como em uma conversa casual
        2. Evite explicar diretamente o significado da palavra
        3. Crie situações cotidianas onde a palavra seria usada naturalmente
        4. Cada frase deve ter no máximo 120 caracteres
        5. As frases devem ser diferentes entre si
        6. Não use aspas ou formatação especial
        7. Retorne apenas as 3 frases, uma por linha, sem numeração ou outros textos
        
        Exemplo de estilo desejado:
        Para a palavra "eloquente":
        - Durante o jantar, fiquei impressionado com o discurso eloquente do professor sobre arte.
        - Maria sempre foi eloquente nas reuniões de trabalho, conquistando a atenção de todos.
        - Seu jeito eloquente de explicar matemática fez toda a turma entender o assunto.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            if not response.choices[0].message.content:
                raise ValueError("Resposta vazia do modelo")
                
            # Processa a resposta para obter as frases
            frases = response.choices[0].message.content.strip().split('\n')
            # Limpa e valida as frases
            frases = [f.strip() for f in frases if f.strip()]
            # Garante que temos exatamente 3 frases
            frases = frases[:3]
            
            # Se não conseguimos 3 frases, complementamos com genéricas
            while len(frases) < 3:
                frases.append(self.gerar_frase_padrao(palavra, len(frases)))
            
            # Se temos o ID da palavra, salvamos as frases no banco
            if palavra_id:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    
                    # Salvamos cada frase nova
                    for frase in frases:
                        cursor.execute(
                            "INSERT INTO frases (palavra_id, frase) VALUES (?, ?)",
                            (palavra_id, frase)
                        )
                    
                    conn.commit()
                    conn.close()
                    
                except Exception as e:
                    print(f"⚠️ Erro ao salvar frases no banco: {str(e)}")
            
            return frases
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar frases: {str(e)}")
            # Retorna frases genéricas em caso de erro
            return [self.gerar_frase_padrao(palavra, i) for i in range(3)]
    
    def gerar_frase_unica(self, palavra: str, definicao: str, categoria: str) -> str:
        """
        Gera uma única frase de exemplo usando a palavra.
        Útil para complementar o conjunto de frases ou gerar exemplos individuais.
        """
        if not self.client:
            return self.gerar_frase_padrao(palavra)
            
        try:
            prompt = f"""
            Gere uma frase em português que use a palavra "{palavra}" em um contexto natural do dia a dia.
            
            Informações sobre a palavra:
            - Definição: {definicao}
            - Categoria: {categoria}
            
            Regras para a frase:
            1. Use a palavra de forma sutil e natural, como em uma conversa casual
            2. Evite explicar diretamente o significado da palavra
            3. Crie uma situação cotidiana onde a palavra seria usada naturalmente
            4. A frase deve ter no máximo 120 caracteres
            5. Não use aspas ou formatação especial
            6. Retorne apenas a frase, sem numeração ou outros textos
            
            Exemplo de estilo desejado:
            Para a palavra "eloquente":
            Durante o jantar, fiquei impressionado com o discurso eloquente do professor sobre arte.
            """
            
            response = self.client.chat.completions.create(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            if not response.choices[0].message.content:
                raise ValueError("Resposta vazia do modelo")
                
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar frase única: {str(e)}")
            return self.gerar_frase_padrao(palavra) 