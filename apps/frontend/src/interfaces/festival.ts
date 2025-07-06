export interface Festival {
  id: number;
  festivalName: string;
  websiteUrl?: string;
  country?: string;
  city?: string;
  dateString?: string;
  contactEmail?: string;
  startDate?: Date;
  endDate?: Date;
  type?: string;
}
