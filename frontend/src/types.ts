export interface Word {
  termo: string;
  categoria: string;
  definicao: string;
  frases: string[];
  dificuldade?: number;
}

export interface GameState {
  currentWord: Word | null;
  score: number;
  totalAttempts: number;
  feedback: {
    show: boolean;
    isCorrect: boolean;
    message: string;
    definicaoCorreta?: string;
  };
  loading: boolean;
}