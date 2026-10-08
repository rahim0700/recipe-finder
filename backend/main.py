from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Recipe Finder API", version="1.0.0")

# Enable CORS for frontend connectivity (Vue Vite typically runs on port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Recipe Finder API! Backend is running successfully."}

@app.get("/api/recipes/search")
async def search_recipes(query: str):
    """Search recipes by name using TheMealDB API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/search.php", params={"s": query})
            data = response.json()
            return data.get("meals") or []
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to recipe provider: {str(e)}")

@app.get("/api/recipes/{meal_id}")
async def get_recipe_details(meal_id: str):
    """Fetch detailed recipe info by its unique ID"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/lookup.php", params={"i": meal_id})
            data = response.json()
            meals = data.get("meals")
            if not meals:
                raise HTTPException(status_code=404, detail="Recipe not found")
            return meals[0]
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to recipe provider: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """Fetch all meal categories from TheMealDB"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/categories.php")
            data = response.json()
            return data.get("categories") or []
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to recipe provider: {str(e)}")

@app.get("/api/recipes/filter")
async def filter_recipes_by_category(category: str):
    """Filter recipes by exact category name safely"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/filter.php", params={"c": category.strip()})
            data = response.json()
            
            meals = data.get("meals")
            if isinstance(meals, list):
                return meals
            return []
        except Exception as e:
            # Catch any unexpected error and return an empty list instead of a 500 crash
            print(f"Error filtering category {category}: {str(e)}")
            return [],