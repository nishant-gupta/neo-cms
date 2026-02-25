import cors from "@fastify/cors";
import helmet from "@fastify/helmet";
import sensible from "@fastify/sensible";
import Fastify, { type FastifyBaseLogger } from "fastify";
import { config } from "./config";
import { registerAssetRoutes } from "./routes/assets";
import { registerHealthRoutes } from "./routes/health";

export function buildApp(logger?: FastifyBaseLogger) {
  const app = Fastify({
    logger: logger ?? { level: config.LOG_LEVEL }
  });

  app.register(helmet);
  app.register(cors, { origin: true });
  app.register(sensible);

  app.setErrorHandler((error, request, reply) => {
    request.log.error({ err: error }, "unhandled_error");
    reply.code(500).send({
      error: "internal_server_error",
      message: "An unexpected error occurred"
    });
  });

  app.setNotFoundHandler((request, reply) => {
    reply.code(404).send({
      error: "not_found",
      path: request.url
    });
  });

  app.register(registerHealthRoutes);
  app.register(registerAssetRoutes);

  return app;
}
