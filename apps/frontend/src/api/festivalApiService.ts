import { Festival } from "@/interfaces/Festival";
import { fetchRequest, sendRequest, deleteRequest, sendFormDataRequest } from "./fetchHelper";
import { Application, ApplicationCreate } from "@/interfaces/Application";

const endpoint = "http://localhost:8000/api/festivals/";

const festivalApiService = {
  async getAllFestivals(): Promise<Festival[]> {
    return fetchRequest<Festival[]>(endpoint);
  },

  async getFestival(festivalId: number): Promise<Festival> {
    return fetchRequest<Festival>(`${endpoint}${festivalId}/`);
  },

  async createFestival(festival: Festival): Promise<Festival> {
    return sendRequest<Festival>(`${endpoint}`, festival, "POST", "Festival successfully created");
  },

  async deleteFestival(festivalId: number) {
    return deleteRequest(`${endpoint}${festivalId}`, "Festival successfully deleted");
  },

  async enrichFestival(festival: Festival): Promise<Festival> {
    return fetchRequest<Festival>(`${endpoint}${festival.id}/enrich/`, {
      method: "POST",
      body: JSON.stringify(festival),
    });
  },

  async updateFestival(festival: Festival): Promise<Festival> {
    return sendRequest<Festival>(`${endpoint}${festival.id}/`, festival, "PUT", "Festival successfully updated");
  },

  async generateEmail(festivalId: number): Promise<{ message: string }> {
    return sendRequest<{ message: string }>(
      `${endpoint}${festivalId}/generate_email/`,
      { message: "" },
      "POST",
      "Email successfully generated"
    );
  },

  async applyToFestival(festivalId: number, application: Application, files: File[], fileFieldName: string): Promise<Application> {
    return sendFormDataRequest<ApplicationCreate, Application>(
      `${endpoint}${festivalId}/apply/`,
      application,
      files,
      fileFieldName,
      "POST",
      "Application successfully sent"
    );
  },
};

export default festivalApiService;
