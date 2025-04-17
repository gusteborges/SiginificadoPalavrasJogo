import React from 'react';

interface ScoreBoardProps {
  score: number;
  totalAttempts: number;
}

export function ScoreBoard({ score, totalAttempts }: ScoreBoardProps) {
  const percentage = totalAttempts > 0 ? (score / totalAttempts) * 100 : 0;

  return (
    <div className="flex items-center justify-center gap-3 sm:gap-4 text-gold-500 text-sm sm:text-base md:text-lg">
      <div className="text-center">
        <p className="font-semibold">Pontos: {score}</p>
      </div>
      <div className="h-4 sm:h-6 w-px bg-gold-500/30" />
      <div className="text-center">
        <p className="font-semibold">Tentativas: {totalAttempts}</p>
      </div>
    </div>
  );
}