import camelcaseKeys from "camelcase-keys";
import { Festival } from "@/interfaces/festival";
import { fetchJson } from "./fetchJson";

const endpoint = "http://localhost:8000/api/festivals/";

const festivalApiSerivice = {
  async getAllFestivals(): Promise<Festival[]> {
    return fetchJson<Festival[]>(endpoint);
  },

  async getFestival(id: string): Promise<Festival> {
    return fetchJson<Festival>(`${endpoint}${id}`);
  },
};

export default festivalApiSerivice;
