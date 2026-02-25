import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { buildApp } from "../src/app";

const app = buildApp();

beforeAll(async () => {
  await app.ready();
});

afterAll(async () => {
  await app.close();
});

describe("signed upload endpoint", () => {
  it("rejects unsupported mime type", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/api/v1/assets/signed-upload-url",
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
      payload: {}
    });

    expect(response.statusCode).toBe(400);
    expect(response.json().error).toBe("validation_error");
  });
});
