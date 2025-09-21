export interface Venue {
  [key: string]: unknown;
  id: number;
  venueName: string;
  websiteUrl?: string;
  country?: string;
  town?: string;
  approximateDate?: string;
  contactEmail?: string;
  contactPerson?: string;
  venueType?: VenueType;
  contacted?: boolean;
  description?: string;
  comments?: string;
}

export enum VenueType {
  THEATRE = "Theatre",
  OPERA_HOUSE = "Opera house",
  CONCERT_HALL = "Concert hall",
  DANCE_STUDIO = "Dance studio",
  MUSIC_VENUE = "Music venue",
  CIRCUS_TENT = "Circus tent",
  PERFORMANCE_SPACE = "Performance space",
  ART_GALLERY = "Art gallery",
  OUTDOOR_STAGE = "Outdoor stage",
  PUPPET_THEATRE = "Puppet theatre",
  CIRCUS_SPACE = "Circus space",
  OTHER = "Other",
  UNKNOWN = "Unknown",
}
