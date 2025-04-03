import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import "./styles/globals.css";
import 'tailwindcss/tailwind.css';

function App() {
  const [palavra, setPalavra] = useState(null);
  const [resposta, setResposta] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [definicaoCompleta, setDefinicaoCompleta] = useState(null);

  const carregarPalavra = useCallback(async () => {
    try {
      setCarregando(true);
      setFeedback(null);
      setDefinicaoCompleta(null);
      setResposta('');
      
      const response = await axios.get('http://localhost:8000/api/palavra-aleatoria');
      setPalavra(response.data);
    } catch (error) {
      setFeedback("❌ Erro ao carregar palavra. Tente recarregar a página.");
    } finally {
      setCarregando(false);
    }
  }, []);

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
      
      setFeedback(response.data.feedback);
      setDefinicaoCompleta(response.data.definicao_correta || null);
    } catch (error) {
      setFeedback("❌ Erro ao verificar resposta. Tente novamente.");
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => { 
    carregarPalavra();
  }, [carregarPalavra]);
  
  return (
    <div className="game">
      <div className="game-container">
        <header className="game-header">
          <h1 className="game-title">Adivinhe o Significado</h1>
        </header>

        {/* Área da palavra */}
        {palavra && (
          <div className="term-display">
            {palavra.termo}
          </div>
        )}

        {/* Área de dica e exemplo */}
        {palavra && (
          <div className="hint-section">
            <p className="hint-category">Dica: {palavra.categoria}</p>
            {palavra.frases?.[0] && (
              <p className="hint-example">Exemplo: "{palavra.frases[0]}"</p>
            )}
          </div>
        )}

        {/* Campo de entrada */}
        <div className="input-container">
          <label htmlFor="meaning-input" className="input-label">
            Digite o significado
          </label>
          <input
            id="meaning-input"
            type="text"
            value={resposta}
            onChange={(e) => setResposta(e.target.value)}
            className="input-field"
            placeholder=""
            onKeyDown={(e) => e.key === 'Enter' && !carregando && verificarResposta()}
            disabled={carregando}
          />
        </div>

        {/* Botões */}
        <div className="buttons-container">
          <button
            onClick={verificarResposta}
            className={`btn btn-primary ${carregando || !resposta.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={carregando || !resposta.trim()}
          >
            Verificar
          </button>
          <button
            onClick={carregarPalavra}
            className="btn btn-secondary"
          >
            Próxima palavra
          </button>
        </div>

        {/* Feedback */}
        {feedback && (
          <div className="feedback-container">
            <div className={`feedback-message ${
              feedback.includes('✅') ? 'feedback-correct' :
              feedback.includes('⚠️') ? 'feedback-present' :
              'feedback-absent'
            }`}>
              <p>{feedback.replace(/[✅⚠️❌]/g, '').trim()}</p>
              {definicaoCompleta && (
                <p className="mt-2 text-sm">Definição correta: {definicaoCompleta}</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;