import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().positive().default(8080),
  LOG_LEVEL: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),
  GCP_PROJECT_ID: z.string().min(1).optional(),
  GCS_ASSETS_BUCKET: z.string().min(1).default("cms-assets-dev"),
  SIGNED_URL_TTL_SECONDS: z.coerce.number().int().positive().max(3600).default(900)
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  throw new Error(
    `Invalid environment configuration: ${parsed.error.issues
      .map((issue) => `${issue.path.join(".")}: ${issue.message}`)
      .join(", ")}`
  );
}

export const config = parsed.data;
