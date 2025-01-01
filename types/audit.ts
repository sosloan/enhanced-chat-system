// This file is part of MinIO Design System
// Copyright (c) 2024 MinIO, Inc.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

export const AUDIT_VERSION = '1';

export interface APIAudit {
  path?: string;
  status?: string;
  method: string;
  statusCode?: number;
  inputBytes: number;
  outputBytes: number;
  timeToFirstByte?: string;
  timeToResponse?: string;
}

export interface ObjectVersion {
  objectName: string;
  versionId?: string;
}

export interface AuditEntry {
  version: string;
  deploymentId?: string;
  time: Date;
  trigger: string;
  api: APIAudit;
  remoteHost?: string;
  requestId: string;
  sessionId?: string;
  userAgent?: string;
  requestClaims?: Record<string, unknown>;
  requestQuery?: Record<string, string>;
  requestHeaders?: Record<string, string>;
  responseHeaders?: Record<string, string>;
  tags?: Record<string, unknown>;
} 