import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  searchRecipes(query) {
    return apiClient.get(`/recipes/search`, { params: { query } });
  },
  getRecipeDetails(id) {
    return apiClient.get(`/recipes/${id}`);
  },
  getCategories() {
    return apiClient.get(`/categories`);
  },
  filterByCategory(category) {
    return apiClient.get(`/recipes/filter`, { params: { category } });
  },
};
