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
import { Profile } from "@/interfaces/entities/Profile";
import { Performance } from "@/interfaces/entities/Performance";

const endpoint = "http://localhost:8000/api/festivals/";

const getAllFestivals = (): Promise<Festival[]> => {
  return fetchRequest<Festival[]>(endpoint);
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

const deleteFestival = (festivalId: number) => {
  return deleteRequest(
    `${endpoint}${festivalId}`,
    "Festival successfully deleted"
  );
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
  return sendRequest<
    { profile: Profile; selectedPerformanceIds: number[] },
    { message: string }
  >(
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
