import React, { useState, useEffect } from 'react';
import type { Word } from '../types';
import { apiService } from '../services/api';

interface GameCardProps {
  word: Word;
  onSubmit: (answer: string) => void;
  feedback: {
    show: boolean;
    isCorrect: boolean;
    message: string;
    definicaoCorreta?: string;
  };
  loading: boolean;
}

export function GameCard({ word, onSubmit, feedback, loading }: GameCardProps) {
  const [answer, setAnswer] = useState('');
  const [frasesRestantes, setFrasesRestantes] = useState(3);
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [frases, setFrases] = useState<string[]>([]);

  // Atualiza as frases quando a palavra muda
  useEffect(() => {
    console.log('Palavra atualizada:', word);
    if (word && word.frases) {
      console.log('Atualizando frases:', word.frases);
      setFrases(word.frases);
      // Calcula frases restantes (não conta a frase padrão)
      const frasesGeradas = Math.max(0, word.frases.length - 1);
      setFrasesRestantes(3 - frasesGeradas);
    } else {
      // Reset do estado quando não há palavra
      setFrases([]);
      setFrasesRestantes(3);
    }
  }, [word]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || loading) return;
    onSubmit(answer);
    setAnswer('');
  };

  const handleGerarFrase = async () => {
    // Protege contra reentrância, ID inválido ou sem frases restantes
    if (gerando || !word.id || frasesRestantes <= 0) {
      return;
    }
  
    setGerando(true);
    setErro(null);
  
    try {
      console.log('Enviando requisição para gerar frase:', {
        palavra_id: word.id,
        palavra: word.termo,
        definicao: word.definicao,
        categoria: word.categoria
      });
  
      const response = await apiService.gerarFrase({
        palavra_id: word.id,
        palavra: word.termo,
        definicao: word.definicao,
        categoria: word.categoria
      });
  
      // Adiciona a nova frase ao array
      setFrases(prev => {
        const novas = [...prev, response.frase];
        console.log('Atualizando frases:', novas);
        return novas;
      });
      // Atualiza o contador de frases restantes
      setFrasesRestantes(response.frases_restantes);
      setErro(null);
  
    } catch (error) {
      console.error('Erro ao gerar frase:', error);
      if (error instanceof Error) {
        setErro(error.message);
      } else {
        setErro('Erro ao gerar frase. Tente novamente.');
      }
  
    } finally {
      // Garante que, independentemente de sucesso ou erro, o flag seja resetado
      setGerando(false);
    }
  };
  
  return (
    <div className="w-full max-w-2xl rounded-xl bg-app-card-light dark:bg-app-card-dark p-4 sm:p-6 shadow-xl transition-all border border-gold-500/30 mx-4">
      <div className="mb-4 sm:mb-6 text-center">
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gold-600 dark:text-gold-500 mb-2 sm:mb-3 break-words">{word.termo}</h2>
        <p className="mt-2 text-base sm:text-lg font-medium text-gold-700 dark:text-gold-300">O que significa esta palavra?</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
        <div>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full rounded-lg border border-gold-500/30 bg-white/90 dark:bg-app-card-dark/50 p-2 sm:p-3 text-gray-800 dark:text-app-text-dark placeholder-gold-600/50 dark:placeholder-gold-500/50 focus:border-gold-500 focus:outline-none focus:ring-2 focus:ring-gold-500/20 text-sm sm:text-base"
            placeholder="Digite sua resposta aqui..."
            rows={3}
            disabled={loading}
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!answer.trim() || loading}
            className="flex-1 rounded-lg bg-gold-600 dark:bg-gold-500 py-2 sm:py-3 px-4 font-semibold text-white dark:text-app-card-dark transition-colors hover:bg-gold-500 dark:hover:bg-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-500 focus:ring-offset-2 disabled:opacity-50 text-sm sm:text-base"
          >
            {loading ? 'Verificando...' : 'Enviar Resposta'}
          </button>

          <button
            type="button"
            onClick={handleGerarFrase}
            disabled={gerando || frasesRestantes <= 0 || word.id === -1}
            className="rounded-lg bg-gold-600/80 dark:bg-gold-500/80 py-2 sm:py-3 px-4 font-semibold text-white dark:text-app-card-dark transition-colors hover:bg-gold-500 dark:hover:bg-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-500 focus:ring-offset-2 disabled:opacity-50 text-sm sm:text-base whitespace-nowrap"
          >
            {gerando ? 'Gerando...' : `Gerar Frase (${frasesRestantes})`}
          </button>
        </div>
      </form>

      {feedback.show && (
        <div
          className={`mt-3 sm:mt-4 flex flex-col items-center justify-center gap-2 rounded-lg p-2 sm:p-3 text-white dark:text-app-card-dark transition-all ${
            feedback.isCorrect ? 'bg-gold-600 dark:bg-gold-500' : 'bg-red-600 dark:bg-red-500'
          }`}
        >
          <p className="font-medium text-sm sm:text-base">{feedback.message}</p>
          {feedback.definicaoCorreta && (
            <p className="mt-1 sm:mt-2 text-xs sm:text-sm opacity-90">Definição correta: {feedback.definicaoCorreta}</p>
          )}
        </div>
      )}

      {erro && (
        <div className="mt-3 text-red-600 dark:text-red-400 text-sm text-center">
          {erro}
        </div>
      )}

      {frases.length > 0 && (
        <div className="mt-4 space-y-2">
          <h3 className="text-lg font-semibold text-gold-600 dark:text-gold-500">Frases de exemplo:</h3>
          <ul className="list-disc pl-5 space-y-1">
            {frases.map((frase, index) => (
              <li key={index} className="text-sm text-gray-800 dark:text-gray-200">
                {frase}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}