import { Festival } from "@/interfaces/Festival";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";

const endpoint = "http://localhost:8000/api/festivals/";

const festivalApiService = {
  async getAllFestivals(): Promise<Festival[]> {
    return fetchRequest<Festival[]>(endpoint);
  },

  async getFestival(id: number): Promise<Festival> {
    return fetchRequest<Festival>(`${endpoint}${id}/`);
  },

  async createFestival(festival: Festival): Promise<Festival> {
    return sendRequest<Festival>(`${endpoint}`, festival, "POST", "Festival successfully created");
  },

  async deleteFestival(id: number) {
    return deleteRequest(`${endpoint}${id}`, "Festival successfully deleted");
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

  async applyToFestival(
    festival: Festival // : Promise<Application>
  ) {
    return fetchRequest<Festival>(`${endpoint}${festival.id}/apply/`, {
      method: "POST",
      body: JSON.stringify(festival),
    });
  },
};

export default festivalApiService;
