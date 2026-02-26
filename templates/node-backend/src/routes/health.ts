import type { FastifyInstance } from "fastify";

export async function registerHealthRoutes(app: FastifyInstance): Promise<void> {
  app.get("/healthz", async () => ({ ok: true }));

  app.get("/readyz", async () => ({
    ok: true,
    uptimeSeconds: Math.round(process.uptime())
  }));
}
