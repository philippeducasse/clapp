import {
  fetchRequest,
  sendRequest,
  deleteRequest,
} from "./fetchHelper";
import {
  Application,
} from "@/interfaces/entities/Application";
import { PaginatedResponse } from "@/interfaces/PaginatedResponse";

const endpoint = "http://localhost:8000/api/applications/";

const getAllApplications = (): Promise<PaginatedResponse<Application>> => {
  return fetchRequest<PaginatedResponse<Application>>(endpoint);
};

const getApplication = (applicationId: number): Promise<Application> => {
  return fetchRequest<Application>(`${endpoint}${applicationId}/`);
};

const createApplication = (application: Application): Promise<Application> => {
  return sendRequest<Application, Application>(
    `${endpoint}`,
    application,
    "POST",
    "Application successfully created"
  );
};

const deleteApplication = (applicationId: number) => {
  return deleteRequest(`${endpoint}${applicationId}`, "Application successfully deleted");
};

const updateApplication = (application: Application): Promise<Application> => {
  return sendRequest<Application, Application>(
    `${endpoint}${application.id}/`,
    application,
    "PUT",
    "Application successfully updated"
  );
};


export const applicationApiService = {
  getAllApplications,
  getApplication,
  createApplication,
  updateApplication,
  deleteApplication,
};
