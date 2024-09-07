import { User } from "@/types"

const API_URL = "http://localhost:5000/api"

export const AuthService = {
  async login(username: string, password: string): Promise<User> {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Login failed')
    }
    return response.json()
  },

  async register(username: string, password: string): Promise<User> {
    const response = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Registration failed')
    }
    return response.json()
  },

  async changePassword(userId: number, newPassword: string): Promise<void> {
    const response = await fetch(`${API_URL}/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ userId, newPassword }),
    });

    if (!response.ok) {
      throw new Error('Failed to change password');
    }
  },

  async addSecretKey(userId: number, provider: string, secretKey: string): Promise<void> {
    const response = await fetch(`${API_URL}/add-secret-key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ userId, provider, secretKey }),
    });
  
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to add secret key');
    }
  }
};