import { useState, useEffect } from 'react';
import { getRandomWord, checkAnswer } from '../../API/api';
import GameCard from '../../components/GameCard';

export default function GamePage() {
  const [currentWord, setCurrentWord] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');

  const loadWord = async () => {
    const { data } = await getRandomWord();
    setCurrentWord(data);
  };

  const handleSubmit = async () => {
    const { data } = await checkAnswer(currentWord.termo, userAnswer);
    alert(data.acerto ? '✅ Acertou!' : '❌ Tente novamente');
    loadWord();
  };

  useEffect(() => { loadWord(); }, []);

  return (
    <div className="game-container">
      <GameCard 
        word={currentWord?.termo} 
        hint={currentWord?.dica}
        answer={userAnswer}
        onAnswerChange={setUserAnswer}
        onSubmit={handleSubmit}
      />
    </div>
  );
}

export default function GameCard({ word, hint, answer, onAnswerChange, onSubmit }) {
    return (
      <div className="card">
        <h2>Adivinhe: {word}</h2>
        {hint && <p className="hint">Dica: {hint}</p>}
        
        <input
          value={answer}
          onChange={(e) => onAnswerChange(e.target.value)}
          placeholder="Seu palpite..."
        />
        
        <button onClick={onSubmit}>
          Verificar
        </button>
      </div>
    );
  }