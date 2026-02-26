import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { buildApp } from "../src/app";

const app = buildApp();
const editorAuthorization = "Bearer mock:editor@example.com";

beforeAll(async () => {
  await app.ready();
});

afterAll(async () => {
  await app.close();
});

describe("signed upload endpoint", () => {
  it("returns 401 when authorization header is missing", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/api/v1/assets/signed-upload-url",
      payload: {
        mimeType: "image/png",
        originalFileName: "hero.png"
      }
    });

    expect(response.statusCode).toBe(401);
    expect(response.json().error).toBe("unauthorized");
  });

  it("returns 403 when user has no assigned role", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/api/v1/assets/signed-upload-url",
      headers: {
        authorization: "Bearer mock:unassigned@example.com"
      },
      payload: {
        mimeType: "image/png",
        originalFileName: "hero.png"
      }
    });

    expect(response.statusCode).toBe(403);
    expect(response.json().error).toBe("forbidden");
  });

  it("rejects unsupported mime type", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/api/v1/assets/signed-upload-url",
      headers: {
        authorization: editorAuthorization
      },
      payload: {
        mimeType: "text/html",
        originalFileName: "index.html"
      }
    });

    expect(response.statusCode).toBe(400);
    expect(response.json().error).toBe("unsupported_mime_type");
  });

  it("returns validation error when required fields are missing", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/api/v1/assets/signed-upload-url",
      headers: {
        authorization: editorAuthorization
      },
      payload: {}
    });

    expect(response.statusCode).toBe(400);
    expect(response.json().error).toBe("validation_error");
  });
});
