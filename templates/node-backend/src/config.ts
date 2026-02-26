import { z } from "zod";

type AuthMode = "google" | "mock" | "disabled";

const defaultAuthMode: AuthMode = process.env.NODE_ENV === "production" ? "google" : "mock";
const defaultEditorEmails = process.env.NODE_ENV === "test" ? "editor@example.com" : "";
const defaultPublisherEmails = process.env.NODE_ENV === "test" ? "publisher@example.com" : "";
const defaultAdminEmails = process.env.NODE_ENV === "test" ? "admin@example.com" : "";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().positive().default(8080),
  LOG_LEVEL: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),
  AUTH_MODE: z.enum(["google", "mock", "disabled"]).default(defaultAuthMode),
  GOOGLE_OAUTH_CLIENT_ID: z.string().min(1).optional(),
  RBAC_EDITOR_EMAILS: z.string().default(defaultEditorEmails),
  RBAC_PUBLISHER_EMAILS: z.string().default(defaultPublisherEmails),
  RBAC_ADMIN_EMAILS: z.string().default(defaultAdminEmails),
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

if (parsed.data.AUTH_MODE === "google" && !parsed.data.GOOGLE_OAUTH_CLIENT_ID) {
  throw new Error("GOOGLE_OAUTH_CLIENT_ID must be set when AUTH_MODE=google");
}

export const config = parsed.data;
