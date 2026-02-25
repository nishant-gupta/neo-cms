import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { buildApp } from "../src/app";

const app = buildApp();

beforeAll(async () => {
  await app.ready();
});

afterAll(async () => {
  await app.close();
});

describe("health routes", () => {
  it("returns 200 for /healthz", async () => {
    const response = await app.inject({
      method: "GET",
      url: "/healthz"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ ok: true });
  });

  it("returns 200 for /readyz", async () => {
    const response = await app.inject({
      method: "GET",
      url: "/readyz"
    });

    expect(response.statusCode).toBe(200);
    expect(response.json().ok).toBe(true);
  });
});
