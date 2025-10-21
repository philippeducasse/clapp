import { Venue } from "@/interfaces/entities/Venue";
import {
  fetchRequest,
  sendRequest,
  deleteRequest,
  sendFormDataRequest,
} from "./fetchHelper";
import {
  Application,
  ApplicationCreate,
} from "@/interfaces/entities/Application";
import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { EntityApiService } from "@/interfaces/api/ApiService";

const endpoint = "http://localhost:8000/api/venues/";

const getAllVenues = (): Promise<PaginatedResponse<Venue>> => {
  return fetchRequest<PaginatedResponse<Venue>>(endpoint);
};

const getVenue = (venueId: number): Promise<Venue> => {
  return fetchRequest<Venue>(`${endpoint}${venueId}/`);
};

const createVenue = (venue: Venue): Promise<Venue> => {
  return sendRequest<Venue, Venue>(
    `${endpoint}`,
    venue,
    "POST",
    "Venue successfully created"
  );
};

const deleteVenue = (venueId: number): Promise<void> => {
  return deleteRequest(`${endpoint}${venueId}`, "Venue successfully deleted");
};

const enrichVenue = (id: number): Promise<Venue> => {
  return fetchRequest<Venue>(`${endpoint}${id}/enrich/`);
};

const updateVenue = (venue: Venue): Promise<Venue> => {
  return sendRequest<Venue, Venue>(
    `${endpoint}${venue.id}/`,
    venue,
    "PUT",
    "Venue successfully updated"
  );
};

const generateEmail = (venueId: number): Promise<{ message: string }> => {
  return sendRequest<{ message: string }, { message: string }>(
    `${endpoint}${venueId}/generate_email/`,
    { message: "" },
    "POST",
    "Email successfully generated"
  );
};

const applyToVenue = (
  venueId: number,
  application: Application,
  files: File[],
  fileFieldName: string
): Promise<Application> => {
  return sendFormDataRequest<ApplicationCreate, Application>(
    `${endpoint}${venueId}/apply/`,
    application,
    files,
    fileFieldName,
    "POST",
    "Application successfully sent"
  );
};

export const venueApiService: EntityApiService<Venue> & {
  getAllVenues: typeof getAllVenues;
  getVenue: typeof getVenue;
  createVenue: typeof createVenue;
  updateVenue: typeof updateVenue;
  deleteVenue: typeof deleteVenue;
  enrichVenue: typeof enrichVenue;
  generateEmail: typeof generateEmail;
  applyToVenue: typeof applyToVenue;
} = {
  // Interface methods
  getAll: getAllVenues,
  get: getVenue,
  create: createVenue,
  update: updateVenue,
  delete: deleteVenue,
  enrich: enrichVenue,
  // Legacy method names for backwards compatibility
  getAllVenues,
  getVenue,
  createVenue,
  updateVenue,
  deleteVenue,
  enrichVenue,
  // Entity-specific methods
  generateEmail,
  applyToVenue,
};
