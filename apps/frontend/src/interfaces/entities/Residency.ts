import { OrganisationContact } from "./OrganisationContact";

export interface Residency {
  [key: string]: unknown;
  id: number;
  name: string;
  websiteUrl?: string;
  country?: string;
  town?: string;
  approximateDate?: string;
  contact?: OrganisationContact[];
  startDate?: Date;
  endDate?: Date;
  applicationType?: string;
  applicationStart?: string;
  applicationEnd?: string;
  applied?: boolean;
  description?: string;
}
