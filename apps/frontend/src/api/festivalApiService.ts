import { Festival } from "@/interfaces/entities/Festival";
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

const endpoint = "/api/festivals/";

const getAllFestivals = (): Promise<Festival[]> => {
  return fetchRequest<Festival[]>(endpoint);
};

const getFestival = (festivalId: number): Promise<Festival> => {
  return fetchRequest<Festival>(`${endpoint}${festivalId}/`);
};

const createFestival = (festival: Festival): Promise<Festival> => {
  return sendRequest<Festival>(
    `${endpoint}`,
    festival,
    "POST",
    "Festival successfully created"
  );
};

const deleteFestival = (festivalId: number) => {
  return deleteRequest(
    `${endpoint}${festivalId}`,
    "Festival successfully deleted"
  );
};

const enrichFestival = (festival: Festival): Promise<Festival> => {
  return fetchRequest<Festival>(`${endpoint}${festival.id}/enrich/`, {
    method: "POST",
    body: JSON.stringify(festival),
  });
};

const updateFestival = (festival: Festival): Promise<Festival> => {
  return sendRequest<Festival>(
    `${endpoint}${festival.id}/`,
    festival,
    "PUT",
    "Festival successfully updated"
  );
};

const generateEmail = (festivalId: number): Promise<{ message: string }> => {
  return sendRequest<{ message: string }>(
    `${endpoint}${festivalId}/generate_email/`,
    { message: "" },
    "POST",
    "Email successfully generated"
  );
};

const applyToFestival = (
  festivalId: number,
  application: Application,
  files: File[],
  fileFieldName: string
): Promise<Application> => {
  return sendFormDataRequest<ApplicationCreate, Application>(
    `${endpoint}${festivalId}/apply/`,
    application,
    files,
    fileFieldName,
    "POST",
    "Application successfully sent"
  );
};

export const festivalApiService = {
  getAllFestivals,
  getFestival,
  createFestival,
  generateEmail,
  enrichFestival,
  applyToFestival,
  updateFestival,
  deleteFestival,
};
