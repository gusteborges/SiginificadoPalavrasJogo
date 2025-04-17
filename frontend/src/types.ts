export interface Word {
  id: number;
  termo: string;
  definicao: string;
  categoria: string;
  frases?: string[];
}

export interface GameState {
  currentWord: Word | null;
  score: number;
  totalAttempts: number;
  loading: boolean;
  feedback: {
    show: boolean;
    isCorrect: boolean;
    message: string;
    definicaoCorreta?: string;
  };
}