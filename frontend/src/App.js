import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [palavra, setPalavra] = useState(null);
  const [resposta, setResposta] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [definicaoCompleta, setDefinicaoCompleta] = useState(null);

  const carregarPalavra = async () => {
    try {
      setCarregando(true);
      setFeedback(null);
      setDefinicaoCompleta(null);
      setResposta('');
      
      const response = await axios.get('http://localhost:8000/api/palavra-aleatoria');
      setPalavra(response.data);
    } catch (error) {
      console.error("Erro detalhado:", error.response?.data || error.message);
      setFeedback("❌ Erro ao carregar palavra. Tente recarregar a página.");
    } finally {
      setCarregando(false);
    }
  };
  
  const verificarResposta = async () => {
    if (!resposta.trim()) {
      setFeedback("❌ Por favor, digite uma resposta");
      return;
    }

    try {
      setCarregando(true);
      setFeedback(null);
      setDefinicaoCompleta(null);
      
      const response = await axios.post('http://localhost:8000/api/verificar', {
        palavra: palavra.termo,
        resposta: resposta.trim()
      });

      console.log("Resposta da API:", response.data); // Para depuração
      
      setFeedback(response.data.feedback);
      setDefinicaoCompleta(response.data.definicao_correta || null);
      
    } catch (error) {
      console.error("Erro detalhado:", {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      setFeedback("❌ Erro ao verificar resposta. Tente novamente.");
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => { 
    carregarPalavra();
  }, []);

  useEffect(() => {
    console.log("Feedback atualizado:", feedback);
    console.log("Definição completa atualizada:", definicaoCompleta);
  }, [feedback, definicaoCompleta]);

  if (!palavra && !feedback) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Adivinhe o Significado</h1>
        
        {palavra && (
          <div className="mb-6">
            <p className="text-lg mb-2">
              <span className="font-semibold">{palavra.termo}</span>
            </p>
            <p className="text-sm text-gray-600 mb-2">Dica: {palavra.categoria}</p>
            
            {palavra.frases?.[0] && (
              <div className="mt-2 text-sm italic bg-gray-50 p-2 rounded">
                <p>Exemplo: "{palavra.frases[0]}"</p>
              </div>
            )}
          </div>
        )}
        
        <input
          type="text"
          value={resposta}
          onChange={(e) => setResposta(e.target.value)}
          className="w-full p-3 border rounded mb-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Digite o significado..."
          onKeyPress={(e) => e.key === 'Enter' && !carregando && verificarResposta()}
          disabled={carregando}
        />
        
        <button
          onClick={verificarResposta}
          className={`w-full py-3 rounded transition-colors ${
            carregando || !resposta.trim() 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
          disabled={carregando || !resposta.trim()}
        >
          {carregando ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processando...
            </span>
          ) : 'Verificar'}
        </button>

        {feedback && (
          <div className={`mt-4 p-3 text-center rounded ${
            feedback.includes('✅') ? 'bg-green-100 text-green-800' :
            feedback.includes('⚠️') ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            <p className="font-medium">{feedback}</p>
            {definicaoCompleta && (
              <p className="mt-2 text-sm">Definição correta: {definicaoCompleta}</p>
            )}
          </div>
        )}

        {palavra && !carregando && (
          <button
            onClick={carregarPalavra}
            className="mt-4 w-full py-2 text-sm text-blue-600 hover:text-blue-800"
          >
            Próxima palavra
          </button>
        )}
      </div>
    </div>
  );
}

export default App;