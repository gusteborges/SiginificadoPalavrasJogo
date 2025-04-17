import React, { useState, useCallback, useEffect } from 'react';
import { Header } from './components/Header';
import { GameCard } from './components/GameCard';
import { ScoreBoard } from './components/ScoreBoard';
import { apiService } from './services/api';
import type { GameState } from './types';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    return savedMode === null ? true : savedMode === 'true';
  });

  const [gameState, setGameState] = useState<GameState>({
    currentWord: null,
    score: 0,
    totalAttempts: 0,
    feedback: {
      show: false,
      isCorrect: false,
      message: '',
    },
    loading: true,
  });

  useEffect(() => {
    localStorage.setItem('darkMode', isDarkMode.toString());
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(prev => !prev);
  };

  // Função para carregar palavra sem useCallback
  const carregarPalavra = async () => {
    try {
      setGameState(prev => ({ ...prev, loading: true }));
      const palavra = await apiService.getPalavraAleatoria();
      
      setGameState(prev => ({
        ...prev,
        currentWord: palavra,
        loading: false,
        feedback: {
          show: false,
          isCorrect: false,
          message: '',
        },
      }));
    } catch (error) {
      console.error('Erro ao carregar palavra:', error);
      
      setGameState(prev => ({
        ...prev,
        loading: false,
        currentWord: null,
        feedback: {
          show: true,
          isCorrect: false,
          message: error instanceof Error ? error.message : 'Erro ao carregar palavra. Tente novamente.',
        },
      }));
    }
  };

  const checkAnswer = async (answer: string) => {
    if (!gameState.currentWord) return;

    try {
      setGameState(prev => ({ ...prev, loading: true }));
      
      const response = await apiService.verificarResposta({
        palavra: gameState.currentWord.termo,
        resposta: answer,
      });

      setGameState(prev => ({
        ...prev,
        score: response.acerto ? prev.score + 1 : prev.score,
        totalAttempts: prev.totalAttempts + 1,
        feedback: {
          show: true,
          isCorrect: response.acerto,
          message: response.feedback,
          definicaoCorreta: response.definicao_correta,
        },
        loading: false,
      }));

      if (response.acerto) {
        // Carrega próxima palavra após 2 segundos em caso de acerto
        setTimeout(() => {
          carregarPalavra();
        }, 2000);
      }
    } catch (error) {
      console.error('Erro ao verificar resposta:', error);
      
      setGameState(prev => ({
        ...prev,
        loading: false,
        feedback: {
          show: true,
          isCorrect: false,
          message: error instanceof Error ? error.message : 'Erro ao verificar resposta. Tente novamente.',
        },
      }));
    }
  };

  // Carrega a primeira palavra apenas uma vez ao montar o componente
  useEffect(() => {
    carregarPalavra();
  }, []); // Array de dependências vazio para executar apenas uma vez

  return (
    <div className={`min-h-screen bg-app-background-light dark:bg-app-background-dark text-app-text-light dark:text-app-text-dark transition-colors duration-300`}>
      <Header onToggleDarkMode={toggleDarkMode} isDarkMode={isDarkMode} />
      
      <main className="container mx-auto flex min-h-screen flex-col items-center justify-center gap-6 px-4 sm:px-6 lg:px-8 pt-16 sm:pt-20 pb-6 sm:pb-8">
        <ScoreBoard score={gameState.score} totalAttempts={gameState.totalAttempts} />
        
        <GameCard
          word={gameState.currentWord || {
            termo: gameState.loading ? 'Carregando...' : 'Erro ao carregar palavra',
            categoria: '',
            definicao: '',
            frases: [],
          }}
          onSubmit={checkAnswer}
          feedback={gameState.feedback}
          loading={gameState.loading}
        />
      </main>
    </div>
  );
}

export default App;