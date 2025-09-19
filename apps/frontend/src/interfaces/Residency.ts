import { ApplicationStatus } from "./Enums";

export interface Residency {
  id: number;
  name: string;
  description: string;
  location: string;
  startDate: string;
  endDate: string;
  status: ApplicationStatus;
  website: string;
  lastUpdated: string;
  hasUpdates: boolean;
  imageUrl: string;
}

export interface ResidencyUpdate {
  id: number;
  name: string;
  description: string;
  location: string;
  startDate: string;
  endDate: string;
  status: ApplicationStatus;
  website: string;
  lastUpdated: string;
  hasUpdates: boolean;
  imageUrl: string;
  diff: ResidencyDiff;
}

export interface ResidencyDiff {
  [key: string]: {
    old: string | boolean;
    new: string | boolean;
  };
}
