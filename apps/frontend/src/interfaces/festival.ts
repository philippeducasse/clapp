export interface Festival {
  id: number;
  festivalName: string;
  websiteUrl?: string;
  country?: string;
  town?: string;
  approximateDate?: string;
  contactEmail?: string;
  contactPerson?: string;
  startDate?: Date;
  endDate?: Date;
  festivalType?: string;
  description?: string;
  applicationType?: string;
  applicationStart?: string;
  applicationEnd?: string;
  applied?: boolean;
}
