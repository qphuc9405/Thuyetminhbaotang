import { defineConfig } from 'vite';

// /mg/* -> backend museum-guide (kho tư liệu có trích nguồn, chatbot RAG, ảnh). Đổi địa chỉ bằng biến môi trường MG_API.
const MG_API = process.env.MG_API || 'http://127.0.0.1:8077';
// /api/* -> backend mẫu của repo (tuỳ chọn). Đổi bằng biến môi trường SAMPLE_API.
const SAMPLE_API = process.env.SAMPLE_API || 'http://127.0.0.1:8000';

export default defineConfig({
  server: {
    proxy: {
      '/mg': { target: MG_API, changeOrigin: true, rewrite: (p) => p.replace(/^\/mg/, '') },
      '/api': SAMPLE_API,
    },
  },
  preview: {
    proxy: {
      '/mg': { target: MG_API, changeOrigin: true, rewrite: (p) => p.replace(/^\/mg/, '') },
    },
  },
});
