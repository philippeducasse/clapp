import { Festival } from "@/interfaces/entities/Festival";
import {
  fetchRequest,
  sendRequest,
  deleteRequest,
  sendFormDataRequest,
  patchRequest,
} from "./fetchHelper";
import { Application, ApplicationCreate } from "@/interfaces/entities/Application";
import { Profile } from "@/interfaces/entities/Profile";
import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { MarkAction } from "@/interfaces/Enums";
import { EntityApiService } from "@/interfaces/api/ApiService";

const endpoint = "http://localhost:8000/api/festivals/";

const getAllFestivals = (): // limit: number = 500,
// offset: number = 0
Promise<PaginatedResponse<Festival>> => {
  return fetchRequest<PaginatedResponse<Festival>>(
    // `${endpoint}?limit=${limit}&offset=${offset}`
    endpoint
  );
};

const getFestival = (festivalId: number): Promise<Festival> => {
  return fetchRequest<Festival>(`${endpoint}${festivalId}/`);
};

const createFestival = (festival: Festival): Promise<Festival> => {
  return sendRequest<Festival, Festival>(
    `${endpoint}`,
    festival,
    "POST",
    "Festival successfully created"
  );
};

const markFestival = (festivalId: number, action: MarkAction): Promise<Festival> => {
  return patchRequest<Festival>(
    `${endpoint}${festivalId}/mark/${action}/`,
    "Festival successfully marked"
  );
};

const deleteFestival = (festivalId: number): Promise<void> => {
  return deleteRequest(`${endpoint}${festivalId}`, "Festival successfully deleted");
};

const enrichFestival = (festivalId: number): Promise<Festival> => {
  return fetchRequest<Festival>(`${endpoint}${festivalId}/enrich/`);
};

const updateFestival = (festival: Festival): Promise<Festival> => {
  return sendRequest<Festival, Festival>(
    `${endpoint}${festival.id}/`,
    festival,
    "PUT",
    "Festival successfully updated"
  );
};

const generateEmail = (
  festivalId: number,
  data: { profile: Profile; selectedPerformanceIds: number[] }
): Promise<{ message: string }> => {
  return sendRequest<{ profile: Profile; selectedPerformanceIds: number[] }, { message: string }>(
    `${endpoint}${festivalId}/generate_email/`,
    data,
    "POST",
    "Email successfully generated"
  );
};

const applyToFestival = (
  festivalId: number,
  application: Application,
  files: File[],
  fileFieldName: string
): Promise<{ message: string; applicationId: number }> => {
  return sendFormDataRequest<ApplicationCreate, { message: string; applicationId: number }>(
    `${endpoint}${festivalId}/apply/`,
    application,
    files,
    fileFieldName,
    "POST",
    "Application successfully sent"
  );
};

export const festivalApiService: EntityApiService<Festival> & {
  getAllFestivals: typeof getAllFestivals;
  getFestival: typeof getFestival;
  createFestival: typeof createFestival;
  updateFestival: typeof updateFestival;
  deleteFestival: typeof deleteFestival;
  markFestival: typeof markFestival;
  enrichFestival: typeof enrichFestival;
  generateEmail: typeof generateEmail;
  applyToFestival: typeof applyToFestival;
} = {
  // Interface methods
  getAll: getAllFestivals,
  get: getFestival,
  create: createFestival,
  update: updateFestival,
  delete: deleteFestival,
  mark: markFestival,
  enrich: enrichFestival,
  // Legacy method names for backwards compatibility
  getAllFestivals,
  getFestival,
  createFestival,
  updateFestival,
  deleteFestival,
  markFestival,
  enrichFestival,
  // Entity-specific methods
  generateEmail,
  applyToFestival,
};
