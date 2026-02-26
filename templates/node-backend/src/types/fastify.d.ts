import "fastify";
import type { AuthUser } from "../auth/rbac";

declare module "fastify" {
  interface FastifyRequest {
    authUser?: AuthUser;
  }
}
