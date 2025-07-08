import camelcaseKeys from "camelcase-keys";
import { Festival } from "@/interfaces/festival";
import { fetchJson } from "./fetchJson";

const endpoint = "http://localhost:8000/api/festivals/";

const festivalApiService = {
  async getAllFestivals(): Promise<Festival[]> {
    return fetchJson<Festival[]>(endpoint);
  },

  async getFestival(id: string): Promise<Festival> {
    return fetchJson<Festival>(`${endpoint}${id}`);
  },

  async enrichFestival(festival: Festival): Promise<any> {
    return fetchJson<Festival>(`${endpoint}${festival.id}/enrich/`, { method: "POST", body: JSON.stringify(festival) });
  },
};

export default festivalApiService;
