import { describe, it, expect, beforeAll } from "vitest";
import { waitForBackend, loginTestUser, TEST_USER, API_BASE, fetchWithAuth } from "./setup";

describe("E2E: Authentication", () => {
  beforeAll(async () => {
    // Ensure backend is ready before running tests
    await waitForBackend();
  });

  it("should login with valid credentials", async () => {
    const response = await fetch(`${API_BASE}/profiles/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: TEST_USER.email,
        password: TEST_USER.password,
      }),
    });

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.email).toBe(TEST_USER.email);
    expect(data.id).toBeDefined();

    // Verify session cookie is set
    const setCookie = response.headers.get("set-cookie");
    expect(setCookie).toBeDefined();
  });

  it("should fail login with invalid credentials", async () => {
    const response = await fetch(`${API_BASE}/profiles/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: TEST_USER.email,
        password: "WrongPassword123!",
      }),
    });

    expect(response.status).toBeGreaterThanOrEqual(400);
  });

  it("should get current profile after login", async () => {
    // Login first
    const loginResponse = await loginTestUser();
    expect(loginResponse.email).toBe(TEST_USER.email);

    // Get current profile
    const profileResponse = await fetchWithAuth(`${API_BASE}/profiles/me`, {
      method: "GET",
    });

    expect(profileResponse.ok).toBe(true);
    const profile = await profileResponse.json();
    expect(profile.email).toBe(TEST_USER.email);
  });

  it("should logout successfully", async () => {
    // Login first
    await loginTestUser();

    // Logout
    const response = await fetchWithAuth(`${API_BASE}/profiles/logout`, {
      method: "POST",
    });

    expect(response.ok).toBe(true);

    // Verify session is invalidated
    const meResponse = await fetchWithAuth(`${API_BASE}/profiles/me`, {
      method: "GET",
    });

    // Should be 401 or redirect
    expect(meResponse.status).toBeGreaterThanOrEqual(400);
  });
});
