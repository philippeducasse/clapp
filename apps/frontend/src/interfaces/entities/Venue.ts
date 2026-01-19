import { OrganisationContact } from "./OrganisationContact";

export interface Venue {
  [key: string]: unknown;
  id: number;
  name: string;
  websiteUrl?: string;
  country?: string;
  town?: string;
  approximateDate?: string;
  contacts?: OrganisationContact[];
  venueType?: VenueType;
  contacted?: boolean;
  description?: string;
  comments?: string;
}

export enum VenueType {
  THEATRE = "THEATRE",
  OPERA_HOUSE = "OPERA_HOUSE",
  CONCERT_HALL = "CONCERT_HALL",
  DANCE_STUDIO = "DANCE_STUDIO",
  MUSIC_VENUE = "MUSIC_VENUE",
  CIRCUS_TENT = "CIRCUS_TENT",
  PERFORMANCE_SPACE = "PERFORMANCE_SPACE",
  ART_GALLERY = "ART_GALLERY",
  OUTDOOR_STAGE = "OUTDOOR_STAGE",
  PUPPET_THEATRE = "PUPPET_THEATRE",
  CIRCUS_SPACE = "CIRCUS_SPACE",
  OTHER = "OTHER",
  UNKNOWN = "UNKNOWN",
}
