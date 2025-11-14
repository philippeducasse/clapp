import { OrganisationContact } from "./OrganisationContact";

export interface Residency {
  [key: string]: unknown;
  id: number;
  name: string;
  location?: string;
  website?: string;
  websiteUrl?: string;
  country?: string;
  town?: string;
  approximateDate?: string;
  contact?: OrganisationContact[];
  startDate?: Date | string;
  endDate?: Date | string;
  applicationType?: string;
  applicationStart?: string;
  applicationEnd?: string;
  applied?: boolean;
  description?: string;
  status?: string;
  lastUpdated?: string;
}
