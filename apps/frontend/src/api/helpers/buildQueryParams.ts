import { GetAllParams } from "@/interfaces/api/ApiService";

export const buildQueryParams = (params?: GetAllParams): string => {
  const queryParams = new URLSearchParams();

  const offset = params?.offset ?? 0;
  const limit = params?.limit ?? 25;

  queryParams.append("offset", String(offset));
  queryParams.append("limit", String(limit));

  if (params?.search) {
    queryParams.append("search", params.search);
  }
  if (params?.filters) {
    Object.entries(params.filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        queryParams.append(`filter_${key}`, String(value));
      }
    });
  }

  return queryParams.toString();
};
