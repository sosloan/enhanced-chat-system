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

import { v4 as uuidv4 } from 'uuid';
import { AUDIT_VERSION, AuditEntry, APIAudit } from '@/types/audit';

export class AuditService {
  private deploymentId: string;
  private auditLogger: (entry: AuditEntry) => Promise<void>;

  constructor(
    deploymentId: string,
    auditLogger: (entry: AuditEntry) => Promise<void>
  ) {
    this.deploymentId = deploymentId;
    this.auditLogger = auditLogger;
  }

  private createEntry(trigger: string, api: APIAudit): AuditEntry {
    return {
      version: AUDIT_VERSION,
      deploymentId: this.deploymentId,
      time: new Date(),
      trigger,
      api,
      requestId: uuidv4(),
    };
  }

  private async logEntry(entry: AuditEntry): Promise<void> {
    try {
      await this.auditLogger(entry);
    } catch (error) {
      console.error('Failed to log audit entry:', error);
    }
  }

  async logChatEvent(
    method: string,
    path: string,
    sessionId?: string,
    claims?: Record<string, unknown>,
    tags?: Record<string, unknown>
  ): Promise<void> {
    const entry = this.createEntry('chat', {
      method,
      path,
      inputBytes: 0,
      outputBytes: 0,
    });

    if (sessionId) {
      entry.sessionId = sessionId;
    }

    if (claims) {
      entry.requestClaims = claims;
    }

    if (tags) {
      entry.tags = tags;
    }

    if (typeof window !== 'undefined') {
      entry.userAgent = window.navigator.userAgent;
    }

    await this.logEntry(entry);
  }

  async logAPIRequest(
    method: string,
    path: string,
    statusCode: number,
    inputBytes: number,
    outputBytes: number,
    timeToResponse: string,
    sessionId?: string,
    headers?: Record<string, string>
  ): Promise<void> {
    const entry = this.createEntry('api', {
      method,
      path,
      statusCode,
      inputBytes,
      outputBytes,
      timeToResponse,
    });

    if (sessionId) {
      entry.sessionId = sessionId;
    }

    if (headers) {
      entry.requestHeaders = headers;
    }

    if (typeof window !== 'undefined') {
      entry.userAgent = window.navigator.userAgent;
      entry.remoteHost = window.location.origin;
    }

    await this.logEntry(entry);
  }

  async logError(
    error: Error,
    method: string,
    path: string,
    sessionId?: string,
    tags?: Record<string, unknown>
  ): Promise<void> {
    const entry = this.createEntry('error', {
      method,
      path,
      status: 'error',
      statusCode: 500,
      inputBytes: 0,
      outputBytes: 0,
    });

    if (sessionId) {
      entry.sessionId = sessionId;
    }

    if (tags) {
      entry.tags = tags;
    }

    entry.tags = {
      ...entry.tags,
      error: {
        message: error.message,
        stack: error.stack,
      },
    };

    if (typeof window !== 'undefined') {
      entry.userAgent = window.navigator.userAgent;
      entry.remoteHost = window.location.origin;
    }

    await this.logEntry(entry);
  }
} 