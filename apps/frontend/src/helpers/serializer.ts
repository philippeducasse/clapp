import { camelCase, snakeCase } from "lodash";
/* eslint-disable @typescript-eslint/no-explicit-any */

export const transformKeysToCamelCase = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map((v) => transformKeysToCamelCase(v));
  } else if (obj !== null && obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const camelKey = camelCase(key);
      result[camelKey] = transformKeysToCamelCase(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
};

export const transformKeysToSnakeCase = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map((v) => transformKeysToSnakeCase(v));
  } else if (obj && obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const snakeKey = snakeCase(key);
      result[snakeKey] = transformKeysToSnakeCase(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
};
