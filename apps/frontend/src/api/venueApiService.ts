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

const endpoint = "http://localhost:8000/api/venues/";

const getAllVenues = (): Promise<Venue[]> => {
  return fetchRequest<Venue[]>(endpoint);
};

const getVenue = (venueId: number): Promise<Venue> => {
  return fetchRequest<Venue>(`${endpoint}${venueId}/`);
};

const createVenue = (venue: Venue): Promise<Venue> => {
  return sendRequest<Venue>(
    `${endpoint}`,
    venue,
    "POST",
    "Venue successfully created"
  );
};

const deleteVenue = (venueId: number) => {
  return deleteRequest(`${endpoint}${venueId}`, "Venue successfully deleted");
};

const enrichVenue = (venue: Venue): Promise<Venue> => {
  return fetchRequest<Venue>(`${endpoint}${venue.id}/enrich/`, {
    method: "POST",
    body: JSON.stringify(venue),
  });
};

const updateVenue = (venue: Venue): Promise<Venue> => {
  return sendRequest<Venue>(
    `${endpoint}${venue.id}/`,
    venue,
    "PUT",
    "Venue successfully updated"
  );
};

const generateEmail = (venueId: number): Promise<{ message: string }> => {
  return sendRequest<{ message: string }>(
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

export const venueApiService = {
  getAllVenues,
  getVenue,
  createVenue,
  generateEmail,
  enrichVenue,
  applyToVenue,
  updateVenue,
  deleteVenue,
};
