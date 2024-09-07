import { Food } from "@/types"

const API_URL = "http://localhost:5000/api"

export const FoodService = {
  async getFoods(userId: number): Promise<Food[]> {
    const response = await fetch(`${API_URL}/foods?userId=${userId}`)
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to fetch foods')
    }
    return response.json()
  },

  async addFood(formData: FormData): Promise<Food> {
    const response = await fetch(`${API_URL}/foods`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to add food')
    }
    return response.json()
  },

  async deleteFood(foodId: number, userId: number): Promise<void> {
    const response = await fetch(`${API_URL}/foods/${foodId}?userId=${userId}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to delete food')
    }
  },

  async recognizeFood(formData: FormData, userId: number): Promise<{ name: string | null, shelfLife: number | null }> {
    formData.append('userId', userId.toString());
    const response = await fetch(`${API_URL}/recognize-food`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to recognize food');
    }
    return response.json();
  }
}