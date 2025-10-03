export interface Performance {
  [key: string]: unknown;
  id: number;
  performanceTitle: string;
  shortDescription?: string;
  trailer?: string;
  length?: string;
  longDescription?: string;
  creationDate?: Date;
  dossier?: string;
  performanceType?: PerformanceType;
  genres?: PerformanceGenre[];
  dossiers?: Dossier[];
}

export interface Dossier {
  [key: string]: unknown;
  id: number;
  file: string;
  uploadedAt: Date;
}

export enum PerformanceType {
  STREET = "STREET",
  INDOOR_STAGE = "INDOOR_STAGE",
  OUTDOOR = "OUTDOOR",
  INSTALLATION = "INSTALLATION",
  WALK_ACT = "WALK_ACT",
  FIRE_SHOW = "FIRE_SHOW",
}

export enum PerformanceGenre {
  CIRCUS = "CIRCUS",
  JUGGLING = "JUGGLING",
  COMEDY = "COMEDY",
  PUPPETRY = "PUPPETRY",
  WALK_ACT = "WALK_ACT",
  FIRE_SHOW = "FIRE_SHOW",
  MUSIC = "MUSIC",
  DANCE = "DANCE",
  THEATRE = "THEATRE",
  MAGIC = "MAGIC",
  INSTALLATION = "INSTALLATION",
  KIDS = "KIDS",
  MULTIMEDIA = "MULTIMEDIA",
}
