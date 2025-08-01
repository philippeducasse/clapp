import { Festival } from "@/interfaces/Festival";
import { fetchJson, sendJson } from "./fetchJson";

const endpoint = "http://localhost:8000/api/festivals/";

const festivalApiService = {
  async getAllFestivals(): Promise<Festival[]> {
    return fetchJson<Festival[]>(endpoint);
  },

  async getFestival(id: string): Promise<Festival> {
    return fetchJson<Festival>(`${endpoint}${id}`);
  },

  async enrichFestival(festival: Festival): Promise<Festival> {
    return fetchJson<Festival>(`${endpoint}${festival.id}/enrich/`, { method: "POST", body: JSON.stringify(festival) });
  },

  async updateFestival(festival: Festival): Promise<Festival> {
    return sendJson<Festival>(`${endpoint}${festival.id}/`, festival, "PUT");
  },
};

export default festivalApiService;
