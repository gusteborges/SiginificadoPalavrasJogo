import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000, // 5 segundos de timeout
  headers: {
    'Content-Type': 'application/json',
  }
});

export interface PalavraResposta {
  id: number;
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

export interface GerarFraseRequest {
  palavra_id: number;
  palavra: string;
  definicao: string;
  categoria: string;
}

export interface GerarFraseResponse {
  frase: string;
  frases_restantes: number;
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

    interface ErrorResponse {
      detail?: string;
    }

    const errorData = axiosError.response.data as ErrorResponse;
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
      console.log('Resposta completa:', {
        status: response.status,
        headers: response.headers,
        data: response.data
      });
      
      // Validação da resposta
      if (!response.data) {
        throw new Error('Resposta vazia do servidor');
      }
      
      if (!response.data.termo || !response.data.definicao) {
        console.error('Dados inválidos recebidos:', response.data);
        throw new Error('Dados inválidos recebidos do servidor');
      }
      
      return response.data;
    } catch (error) {
      console.error('Erro detalhado ao buscar palavra aleatória:', {
        error,
        isAxiosError: axios.isAxiosError(error),
        message: error instanceof Error ? error.message : 'Erro desconhecido',
        stack: error instanceof Error ? error.stack : undefined
      });
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

  gerarFrase: async (request: GerarFraseRequest): Promise<GerarFraseResponse> => {
    try {
      console.log('Gerando nova frase para a palavra:', request.palavra);
      const response = await api.post<GerarFraseResponse>('/gerar-frase', request);
      console.log('Frase gerada:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar frase:', error);
      throw handleApiError(error);
    }
  },
}; 