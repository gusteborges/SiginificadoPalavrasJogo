import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000', // Confirme a porta do seu back-end
  timeout: 5000,
});

export const getRandomWord = () => API.get('/api/palavra-aleatoria');