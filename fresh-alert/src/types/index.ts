export interface Food {
  id: number;
  name: string;
  productionDate: string;
  shelfLife: number;
  expirationDate: string;
  daysLeft: number;
  userId: number;
}

export interface User {
  id: number;
  username: string;
}