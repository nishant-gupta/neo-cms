import { Storage } from "@google-cloud/storage";
import { randomUUID } from "node:crypto";
import { config } from "../config";

const storage = new Storage({ projectId: config.GCP_PROJECT_ID });

const allowedMimeTypes = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/avif",
  "application/pdf",
  "video/mp4"
]);

export function isAllowedMimeType(mimeType: string): boolean {
  return allowedMimeTypes.has(mimeType);
}

export async function createSignedUploadUrl(input: {
  mimeType: string;
  originalFileName: string;
}): Promise<{ signedUrl: string; objectPath: string; expiresInSeconds: number }> {
  const safeName = input.originalFileName.replace(/[^a-zA-Z0-9._-]/g, "_");
  const objectPath = `uploads/${new Date().toISOString().slice(0, 10)}/${randomUUID()}-${safeName}`;
  const file = storage.bucket(config.GCS_ASSETS_BUCKET).file(objectPath);
  const expiresInSeconds = config.SIGNED_URL_TTL_SECONDS;

  const [signedUrl] = await file.getSignedUrl({
    version: "v4",
    action: "write",
    expires: Date.now() + expiresInSeconds * 1000,
    contentType: input.mimeType
  });

  return { signedUrl, objectPath, expiresInSeconds };
}
