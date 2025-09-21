export interface Festival {
  [key: string]: unknown;
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
  festivalType?: FestivalType;
  applicationType?: string;
  applicationStart?: string;
  applicationEnd?: string;
  applied?: boolean;
  description?: string;
}

export enum FestivalType {
  STREET = "STREET",
  PUPPET = "PUPPET",
  JUGGLING_CONVENTION = "JUGGLING_CONVENTION",
  CIRCUS = "CIRCUS",
  MUSIC = "MUSIC",
  THEATRE = "THEATRE",
  DANCE = "DANCE",
  OTHER = "OTHER",
}

export enum ApplicationType {
  EMAIL = "EMAIL",
  FORM = "FORM",
  OTHER = "OTHER",
  UNKNOWN = "UNKNOWN",
}
