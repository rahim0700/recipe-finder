<script setup>
import { ref, onMounted } from 'vue';
import api from './services/api';

const searchQuery = ref('');
const recipes = ref([]);
const categories = ref([]);
const selectedCategory = ref(null);
const loading = ref(false);
const error = ref(null);
const selectedRecipe = ref(null);

const favorites = ref([]);
const activeTab = ref('search');

onMounted(async () => {
  const savedFavorites = localStorage.getItem('recipe_favorites');
  if (savedFavorites) {
    favorites.value = JSON.parse(savedFavorites);
  }

  try {
    const catResponse = await api.getCategories();
    const allCategories = catResponse.data || [];
    
    // Exclude categories with inconsistent public API endpoints
    const excludedCategories = ['Miscellaneous', 'Dessert', 'Side', 'Starter'];
    categories.value = allCategories.filter(cat => !excludedCategories.includes(cat.strCategory));
  } catch (err) {
    console.error('Failed to load categories', err);
  }

  // Load default recipes on start
  searchQuery.value = 'chicken';
  searchRecipes();
});

const searchRecipes = async () => {
  activeTab.value = 'search';
  selectedCategory.value = null;
  if (!searchQuery.value.trim()) return;
  loading.value = true;
  error.value = null;
  try {
    const response = await api.searchRecipes(searchQuery.value);
    recipes.value = response.data || [];
  } catch (err) {
    error.value = 'Failed to fetch recipes. Make sure the FastAPI backend is running.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const filterByCategory = async (categoryName) => {
  activeTab.value = 'search';
  selectedCategory.value = categoryName;
  searchQuery.value = '';
  loading.value = true;
  error.value = null;
  try {
    const response = await api.filterByCategory(categoryName);
    recipes.value = response.data || [];
  } catch (err) {
    error.value = 'Failed to filter recipes by category.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const fetchDetails = async (id) => {
  try {
    const response = await api.getRecipeDetails(id);
    selectedRecipe.value = response.data;
  } catch (err) {
    console.error('Failed to fetch recipe details', err);
  }
};

const toggleFavorite = (recipe, event) => {
  if (event) event.stopPropagation();
  const index = favorites.value.findIndex(item => item.idMeal === recipe.idMeal);
  if (index === -1) {
    favorites.value.push(recipe);
  } else {
    favorites.value.splice(index, 1);
  }
  localStorage.setItem('recipe_favorites', JSON.stringify(favorites.value));
};

const isFavorite = (idMeal) => {
  return favorites.value.some(item => item.idMeal === idMeal);
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-800">
    <!-- Header -->
    <header class="bg-orange-600 text-white shadow-md py-6 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-3xl font-bold mb-2">🍳 Recipe Finder</h1>
        <p class="text-orange-100">Discover delicious meals powered by FastAPI & Vue</p>
        
        <!-- Navigation Tabs -->
        <div class="mt-4 flex justify-center gap-4">
          <button 
            @click="activeTab = 'search'"
            :class="activeTab === 'search' ? 'bg-orange-800 text-white' : 'bg-orange-700/50 text-orange-200 hover:bg-orange-700'"
            class="px-4 py-2 rounded-lg font-medium transition shadow-sm"
          >
            Search & Categories
          </button>
          <button 
            @click="activeTab = 'favorites'"
            :class="activeTab === 'favorites' ? 'bg-orange-800 text-white' : 'bg-orange-700/50 text-orange-200 hover:bg-orange-700'"
            class="px-4 py-2 rounded-lg font-medium transition shadow-sm flex items-center gap-2"
          >
            ❤️ Favorites <span class="bg-orange-900 text-xs px-2 py-0.5 rounded-full">{{ favorites.length }}</span>
          </button>
        </div>

        <!-- Search Bar -->
        <div v-if="activeTab === 'search'" class="mt-6 flex justify-center gap-2">
          <input 
            v-model="searchQuery" 
            @keyup.enter="searchRecipes"
            type="text" 
            placeholder="Search for recipes (e.g., pasta, chicken)..." 
            class="px-4 py-3 rounded-lg w-full max-w-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-orange-400 shadow-sm"
          />
          <button 
            @click="searchRecipes"
            class="bg-orange-800 hover:bg-orange-900 px-6 py-3 rounded-lg font-semibold transition shadow-sm"
          >
            Search
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-4 py-8">
      
      <!-- SEARCH & CATEGORIES TAB VIEW -->
      <div v-if="activeTab === 'search'">
        
        <!-- Category Horizontal Scroll Bar -->
        <div class="mb-8">
          <h2 class="text-lg font-bold text-gray-700 mb-3">Filter by Category</h2>
          <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
            <button 
              v-for="cat in categories" 
              :key="cat.idCategory"
              @click="filterByCategory(cat.strCategory)"
              :class="selectedCategory === cat.strCategory ? 'bg-orange-600 text-white shadow-md' : 'bg-white text-gray-700 hover:bg-orange-50 border border-gray-200'"
              class="px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition"
            >
              {{ cat.strCategory }}
            </button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-12 text-gray-500 text-lg">Loading recipes...</div>
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 text-center">{{ error }}</div>
        
        <div v-if="!loading && recipes.length === 0" class="text-center py-12 text-gray-500 text-lg">
          No recipes found for this selection. Try another category!
        </div>

        <!-- Recipe Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          <div 
            v-for="recipe in recipes" 
            :key="recipe.idMeal"
            @click="fetchDetails(recipe.idMeal)"
            class="bg-white rounded-xl shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition transform hover:-translate-y-1 relative group"
          >
            <img :src="recipe.strMealThumb" :alt="recipe.strMeal" class="w-full h-48 object-cover" />
            
            <button 
              @click="toggleFavorite(recipe, $event)"
              class="absolute top-3 right-3 bg-white/90 hover:bg-white p-2 rounded-full shadow transition"
              title="Save to Favorites"
            >
              <span v-if="isFavorite(recipe.idMeal)" class="text-red-500 text-lg">❤️</span>
              <span v-else class="text-gray-400 hover:text-red-500 text-lg">🤍</span>
            </button>

            <div class="p-4">
              <span class="text-xs font-semibold text-orange-600 uppercase tracking-wider">{{ selectedCategory || 'Recipe' }}</span>
              <h3 class="font-bold text-lg text-gray-900 mt-1 truncate">{{ recipe.strMeal }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- FAVORITES TAB VIEW -->
      <div v-if="activeTab === 'favorites'">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Your Saved Recipes</h2>
        
        <div v-if="favorites.length === 0" class="text-center py-12 bg-white rounded-xl shadow-sm text-gray-500 text-lg">
          You haven't saved any favorite recipes yet. Click the heart icon on any recipe to save it here!
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          <div 
            v-for="recipe in favorites" 
            :key="recipe.idMeal"
            @click="fetchDetails(recipe.idMeal)"
            class="bg-white rounded-xl shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition transform hover:-translate-y-1 relative"
          >
            <img :src="recipe.strMealThumb" :alt="recipe.strMeal" class="w-full h-48 object-cover" />
            
            <button 
              @click="toggleFavorite(recipe, $event)"
              class="absolute top-3 right-3 bg-white/90 hover:bg-white p-2 rounded-full shadow transition"
            >
              <span class="text-red-500 text-lg">❤️</span>
            </button>

            <div class="p-4">
              <span class="text-xs font-semibold text-orange-600 uppercase tracking-wider">Favorite</span>
              <h3 class="font-bold text-lg text-gray-900 mt-1 truncate">{{ recipe.strMeal }}</h3>
            </div>
          </div>
        </div>
      </div>

    </main>

    <!-- Recipe Detail Modal -->
    <div v-if="selectedRecipe" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 relative">
        <button 
          @click="selectedRecipe = null"
          class="absolute top-4 right-4 bg-gray-200 hover:bg-gray-300 rounded-full w-8 h-8 flex items-center justify-center font-bold text-gray-700"
        >
          ✕
        </button>

        <img :src="selectedRecipe.strMealThumb" :alt="selectedRecipe.strMeal" class="w-full h-64 object-cover rounded-xl shadow-md mb-6" />
        
        <div class="flex justify-between items-start mb-2">
          <h2 class="text-2xl font-bold text-gray-900">{{ selectedRecipe.strMeal }}</h2>
          <button 
            @click="toggleFavorite(selectedRecipe)"
            class="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition"
          >
            <span>{{ isFavorite(selectedRecipe.idMeal) ? '❤️ Remove Favorite' : '🤍 Save Favorite' }}</span>
          </button>
        </div>

        <div class="flex gap-4 text-sm text-gray-600 mb-4">
          <span class="bg-orange-100 text-orange-800 px-3 py-1 rounded-full font-medium">Category: {{ selectedRecipe.strCategory }}</span>
          <span class="bg-gray-100 text-gray-800 px-3 py-1 rounded-full font-medium">Area: {{ selectedRecipe.strArea }}</span>
        </div>

        <h3 class="font-semibold text-lg text-gray-800 mb-2">Instructions</h3>
        <p class="text-gray-600 text-sm whitespace-pre-line leading-relaxed bg-gray-50 p-4 rounded-xl mb-6">{{ selectedRecipe.strInstructions }}</p>

        <button 
          @click="selectedRecipe = null"
          class="w-full bg-orange-600 hover:bg-orange-700 text-white font-semibold py-3 rounded-xl transition"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>