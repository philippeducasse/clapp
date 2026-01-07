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
  contacts?: OrganisationContact[];
  startDate?: Date | string;
  endDate?: Date | string;
  applicationType?: string;
  applicationStart?: string;
  applicationEnd?: string;
  applied?: boolean;
  description?: string;
  comments?: string;
  status?: string;
  tag?: string;
  lastUpdated?: string;
}
