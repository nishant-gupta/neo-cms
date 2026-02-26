import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { buildApp } from "../src/app";

const app = buildApp();

beforeAll(async () => {
  await app.ready();
});

afterAll(async () => {
  await app.close();
});

describe("authentication and role checks", () => {
  it("returns profile details for editor token on /api/v1/auth/me", async () => {
    const response = await app.inject({
      method: "GET",
      url: "/api/v1/auth/me",
      headers: {
        authorization: "Bearer mock:editor@example.com"
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json().user.email).toBe("editor@example.com");
    expect(response.json().user.role).toBe("editor");
  });

  it("returns 403 for editor on admin-only endpoint", async () => {
    const response = await app.inject({
      method: "GET",
      url: "/api/v1/admin/access-check",
      headers: {
        authorization: "Bearer mock:editor@example.com"
      }
    });

    expect(response.statusCode).toBe(403);
    expect(response.json().error).toBe("forbidden");
  });

  it("returns 200 for admin on admin-only endpoint", async () => {
    const response = await app.inject({
      method: "GET",
      url: "/api/v1/admin/access-check",
      headers: {
        authorization: "Bearer mock:admin@example.com"
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json().ok).toBe(true);
  });
});
