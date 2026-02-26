import type { FastifyInstance } from "fastify";
import { requireRoles } from "../auth/guard";

export async function registerAuthRoutes(app: FastifyInstance): Promise<void> {
  app.get(
    "/api/v1/auth/me",
    {
      preHandler: [requireRoles(["editor"])]
    },
    async (request) => {
      return {
        user: request.authUser
      };
    }
  );

  app.get(
    "/api/v1/admin/access-check",
    {
      preHandler: [requireRoles(["admin"])]
    },
    async () => {
      return {
        ok: true
      };
    }
  );
}
