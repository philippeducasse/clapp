import camelcaseKeys from "camelcase-keys";
import snakecaseKeys from "snakecase-keys";

export async function fetchJson<T = unknown>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  const json = await res.json();
  return camelcaseKeys(json, { deep: true });
}

export async function sendJson<T = unknown>(
  url: string,
  data: Record<string, unknown>,
  method: "POST" | "PUT" | "PATCH" = "POST"
): Promise<T> {
  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(snakecaseKeys(data, { deep: true })),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Failed to ${method} ${url}: ${res.status} - ${error}`);
  }

  const json = await res.json();
  return json;
}
