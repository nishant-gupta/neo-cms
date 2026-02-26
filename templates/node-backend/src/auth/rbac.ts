import { config } from "../config";

export type UserRole = "editor" | "publisher" | "admin";

export interface AuthUser {
  sub: string;
  email: string;
  role: UserRole;
}

const roleRank: Record<UserRole, number> = {
  editor: 1,
  publisher: 2,
  admin: 3
};

function parseEmailCsv(value: string): Set<string> {
  return new Set(
    value
      .split(",")
      .map((entry) => entry.trim().toLowerCase())
      .filter(Boolean)
  );
}

const editorEmails = parseEmailCsv(config.RBAC_EDITOR_EMAILS);
const publisherEmails = parseEmailCsv(config.RBAC_PUBLISHER_EMAILS);
const adminEmails = parseEmailCsv(config.RBAC_ADMIN_EMAILS);

export function resolveRoleForEmail(email: string): UserRole | null {
  const normalized = email.trim().toLowerCase();

  if (adminEmails.has(normalized)) {
    return "admin";
  }

  if (publisherEmails.has(normalized)) {
    return "publisher";
  }

  if (editorEmails.has(normalized)) {
    return "editor";
  }

  return null;
}

export function canAccessAnyRequiredRole(userRole: UserRole, requiredRoles: UserRole[]): boolean {
  const userRank = roleRank[userRole];
  return requiredRoles.some((requiredRole) => userRank >= roleRank[requiredRole]);
}
