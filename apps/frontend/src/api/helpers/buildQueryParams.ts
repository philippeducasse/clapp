import { GetAllParams } from "@/interfaces/api/ApiService";
import { snakeCase } from "lodash";

/**
 * Limit used when no explicit `limit` is given: list endpoints return every row
 * and tables paginate client-side.
 */
export const FETCH_ALL_LIMIT = 10000;

export const buildQueryParams = (params?: GetAllParams): string => {
  const queryParams = new URLSearchParams();

  const offset = params?.offset ?? 0;
  const limit = params?.limit ?? FETCH_ALL_LIMIT;

  queryParams.append("offset", String(offset));
  queryParams.append("limit", String(limit));

  if (params?.search) {
    queryParams.append("search", params.search);
  }
  if (params?.filters) {
    Object.entries(params.filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        const snakeKey = snakeCase(key);
        queryParams.append(snakeKey, String(value));
      }
    });
  }

  return queryParams.toString();
};
