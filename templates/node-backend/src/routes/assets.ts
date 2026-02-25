import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { createSignedUploadUrl, isAllowedMimeType } from "../services/signedUpload";

const signedUploadRequestSchema = z.object({
  mimeType: z.string().min(1),
  originalFileName: z.string().min(1).max(255)
});

export async function registerAssetRoutes(app: FastifyInstance): Promise<void> {
  app.post("/api/v1/assets/signed-upload-url", async (request, reply) => {
    const parsed = signedUploadRequestSchema.safeParse(request.body);

    if (!parsed.success) {
      return reply.code(400).send({
        error: "validation_error",
        details: parsed.error.flatten()
      });
    }

    if (!isAllowedMimeType(parsed.data.mimeType)) {
      return reply.code(400).send({
        error: "unsupported_mime_type",
        allowed: [
          "image/jpeg",
          "image/png",
          "image/webp",
          "image/avif",
          "application/pdf",
          "video/mp4"
        ]
      });
    }

    const payload = await createSignedUploadUrl(parsed.data);

    return reply.code(201).send(payload);
  });
}
