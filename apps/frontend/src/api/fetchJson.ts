import { transformKeysToCamelCase, transformKeysToSnakeCase } from "@/helpers/serializer";
import { toast } from "sonner";

export const fetchJson = async <T = unknown>(url: string, options?: RequestInit): Promise<T> => {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    toast.error(`Error: ${text}`);
    throw new Error(`Failed to fetch ${url}: ${res.status}`);
  }
  const json = await res.json();
  return transformKeysToCamelCase(json);
};

export const sendJson = async <T = unknown>(
  url: string,
  data: Record<string, unknown>,
  method: "POST" | "PUT" | "PATCH" = "POST",
  toastMessage?: string
): Promise<T> => {
  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(transformKeysToSnakeCase(data)),
  });
  if (!res.ok) {
    const error = await res.text();
    toast.error(`Error: ${error}`);
    throw new Error(`Failed to ${method} ${url}: ${res.status} - ${error}`);
  }
  const json = await res.json();
  toast.success(toastMessage ?? "Success");
  return json;
};
