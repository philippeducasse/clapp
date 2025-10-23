import { Venue } from "@/interfaces/entities/Venue";
import {
  fetchRequest,
  sendRequest,
  deleteRequest,
  sendFormDataRequest,
  patchRequest,
} from "./fetchHelper";
import { Application, ApplicationCreate } from "@/interfaces/entities/Application";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { TagAction } from "@/interfaces/Enums";
import { EntityApiService } from "@/interfaces/api/ApiService";

const endpoint = "http://localhost:8000/api/venues/";

const getAll = (): Promise<PaginatedResponse<Venue>> => {
  return fetchRequest<PaginatedResponse<Venue>>(endpoint);
};

const get = (venueId: number): Promise<Venue> => {
  return fetchRequest<Venue>(`${endpoint}${venueId}/`);
};

const create = (venue: Venue): Promise<Venue> => {
  return sendRequest<Venue, Venue>(`${endpoint}`, venue, "POST", "Venue successfully created");
};

const remove = (venueId: number): Promise<void> => {
  return deleteRequest(`${endpoint}${venueId}`, "Venue successfully deleted");
};

const tag = (venueId: number, action: TagAction): Promise<Venue> => {
  return patchRequest<Venue>(`${endpoint}${venueId}/tag/${action}/`, "Venue successfully tagged");
};

const enrich = (id: number): Promise<Venue> => {
  return fetchRequest<Venue>(`${endpoint}${id}/enrich/`);
};

const update = (venue: Venue): Promise<Venue> => {
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

const apply = (
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

export const venueApiService: EntityApiService<Venue> = {
  getAll,
  get,
  create,
  update,
  remove,
  tag,
  enrich,
  apply,
  generateEmail,
};
