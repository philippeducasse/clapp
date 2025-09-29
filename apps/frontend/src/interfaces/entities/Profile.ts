export interface Profile {
  [key: string]: unknown;
  id: number;
  email: string;
  firstName?: string;
  lastName?: string;
  artistName?: string;
  companyName?: string;
  personalWebsite?: string;
  age?: number;
  location?: string;
  nationality?: string;
  instagramProfile?: string;
  facebookProfile?: string;
  tiktokProfile?: string;
}
