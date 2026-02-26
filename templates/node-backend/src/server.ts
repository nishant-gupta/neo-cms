import { config } from "./config";
import { buildApp } from "./app";

async function start() {
  const app = buildApp();

  const shutdown = async (signal: string) => {
    app.log.info({ signal }, "shutdown_signal_received");
    await app.close();
    process.exit(0);
  };

  process.on("SIGINT", () => void shutdown("SIGINT"));
  process.on("SIGTERM", () => void shutdown("SIGTERM"));

  try {
    await app.listen({
      host: "0.0.0.0",
      port: config.PORT
    });

    app.log.info(
      {
        env: config.NODE_ENV,
        port: config.PORT
      },
      "server_started"
    );
  } catch (error) {
    app.log.error({ err: error }, "server_start_failed");
    process.exit(1);
  }
}

void start();
