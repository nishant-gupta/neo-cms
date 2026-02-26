import type { preHandlerAsyncHookHandler } from "fastify";
import { OAuth2Client } from "google-auth-library";
import { config } from "../config";
import { canAccessAnyRequiredRole, resolveRoleForEmail, type AuthUser, type UserRole } from "./rbac";

const oauthClient = new OAuth2Client(config.GOOGLE_OAUTH_CLIENT_ID);

class AuthError extends Error {
  public readonly code: string;
  public readonly statusCode: number;

  constructor(statusCode: number, code: string, message: string) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
  }
}

function getBearerToken(authorizationHeader?: string): string {
  if (!authorizationHeader) {
    throw new AuthError(401, "unauthorized", "Missing Authorization header");
  }

  const [scheme, token] = authorizationHeader.split(" ");

  if (scheme?.toLowerCase() !== "bearer" || !token) {
    throw new AuthError(401, "unauthorized", "Authorization header must use Bearer token");
  }

  return token;
}

function authenticateMockToken(token: string): { sub: string; email: string } {
  if (!token.startsWith("mock:")) {
    throw new AuthError(401, "unauthorized", "Invalid mock token format");
  }

  const email = token.slice(5).trim().toLowerCase();

  if (!email.includes("@")) {
    throw new AuthError(401, "unauthorized", "Mock token must include a valid email");
  }

  return {
    sub: `mock-${email}`,
    email
  };
}

async function authenticateGoogleToken(token: string): Promise<{ sub: string; email: string }> {
  try {
    const ticket = await oauthClient.verifyIdToken({
      idToken: token,
      audience: config.GOOGLE_OAUTH_CLIENT_ID
    });

    const payload = ticket.getPayload();
    const email = payload?.email?.trim().toLowerCase();

    if (!payload?.sub || !email || payload.email_verified !== true) {
      throw new AuthError(401, "unauthorized", "Token must include a verified Google account email");
    }

    return {
      sub: payload.sub,
      email
    };
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }

    throw new AuthError(401, "unauthorized", "Google OAuth token verification failed");
  }
}

async function authenticateRequest(authorizationHeader?: string): Promise<{ sub: string; email: string }> {
  if (config.AUTH_MODE === "disabled") {
    return {
      sub: "system",
      email: "system@local"
    };
  }

  const token = getBearerToken(authorizationHeader);

  if (config.AUTH_MODE === "mock") {
    return authenticateMockToken(token);
  }

  return authenticateGoogleToken(token);
}

export function requireRoles(requiredRoles: UserRole[]): preHandlerAsyncHookHandler {
  return async (request, reply) => {
    try {
      const identity = await authenticateRequest(request.headers.authorization);
      const role = resolveRoleForEmail(identity.email);

      if (!role) {
        return reply.code(403).send({
          error: "forbidden",
          message: "Authenticated user does not have an assigned role"
        });
      }

      if (!canAccessAnyRequiredRole(role, requiredRoles)) {
        return reply.code(403).send({
          error: "forbidden",
          message: "Insufficient role for this operation"
        });
      }

      request.authUser = {
        sub: identity.sub,
        email: identity.email,
        role
      } satisfies AuthUser;
    } catch (error) {
      if (error instanceof AuthError) {
        return reply.code(error.statusCode).send({
          error: error.code,
          message: error.message
        });
      }

      request.log.error({ err: error }, "auth_guard_failed");
      return reply.code(500).send({
        error: "internal_server_error",
        message: "An unexpected error occurred"
      });
    }
  };
}
