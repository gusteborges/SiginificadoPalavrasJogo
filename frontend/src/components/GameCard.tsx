import React, { useState } from 'react';
import type { Word } from '../types';

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || loading) return;
    onSubmit(answer);
    setAnswer('');
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

        <button
          type="submit"
          disabled={!answer.trim() || loading}
          className="w-full rounded-lg bg-gold-600 dark:bg-gold-500 py-2 sm:py-3 px-4 font-semibold text-white dark:text-app-card-dark transition-colors hover:bg-gold-500 dark:hover:bg-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-500 focus:ring-offset-2 disabled:opacity-50 text-sm sm:text-base"
        >
          {loading ? 'Verificando...' : 'Enviar Resposta'}
        </button>
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
    </div>
  );
}