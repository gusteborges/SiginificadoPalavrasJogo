import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000, // 5 segundos de timeout
  headers: {
    'Content-Type': 'application/json',
  }
});

export interface PalavraResposta {
  termo: string;
  categoria: string;
  definicao: string;
  frases: string[];
  dificuldade?: number;
}

export interface VerificacaoRequest {
  palavra: string;
  resposta: string;
}

export interface VerificacaoResposta {
  acerto: boolean;
  similaridade: number;
  definicao_correta?: string;
  feedback: string;
}

// Função auxiliar para tratar erros
const handleApiError = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    console.error('Detalhes do erro:', {
      message: axiosError.message,
      status: axiosError.response?.status,
      data: axiosError.response?.data,
      config: {
        url: axiosError.config?.url,
        method: axiosError.config?.method,
      }
    });

    if (axiosError.response?.status === 404) {
      throw new Error('Nenhuma palavra encontrada no banco de dados.');
    }
    
    if (axiosError.code === 'ECONNABORTED') {
      throw new Error('Tempo limite de conexão excedido. Verifique se o backend está rodando.');
    }

    if (!axiosError.response) {
      throw new Error('Não foi possível conectar ao servidor. Verifique se o backend está rodando.');
    }

    const errorData = axiosError.response.data as { detail?: string };
    throw new Error(`Erro na API: ${errorData.detail || axiosError.message}`);
  }
  
  throw new Error('Erro inesperado ao comunicar com o servidor.');
};

// Interceptor para logging
api.interceptors.request.use(request => {
  console.log('Starting Request:', request.url);
  return request;
});

api.interceptors.response.use(
  response => {
    console.log('Response:', response.data);
    return response;
  },
  error => {
    console.error('API Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data
    });
    throw error;
  }
);

export const apiService = {
  getPalavraAleatoria: async (): Promise<PalavraResposta> => {
    try {
      console.log('Iniciando requisição para buscar palavra aleatória...');
      const response = await api.get<PalavraResposta>('/palavra-aleatoria');
      console.log('Palavra recebida:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar palavra aleatória:', error);
      throw handleApiError(error);
    }
  },

  verificarResposta: async (request: VerificacaoRequest): Promise<VerificacaoResposta> => {
    try {
      console.log('Enviando resposta para verificação:', request);
      const response = await api.post<VerificacaoResposta>('/verificar', request);
      console.log('Resultado da verificação:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erro ao verificar resposta:', error);
      throw handleApiError(error);
    }
  },
}; 