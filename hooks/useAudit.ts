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

import { useCallback, useContext } from 'react';
import { AuditService } from '@/lib/audit';

// Create a context and provider in a separate file if needed
const defaultAuditLogger = async (entry: any) => {
  console.log('Audit Entry:', entry);
};

const auditService = new AuditService(
  process.env.NEXT_PUBLIC_DEPLOYMENT_ID || 'local',
  defaultAuditLogger
);

export const useAudit = () => {
  const logChatEvent = useCallback(
    async (
      method: string,
      path: string,
      sessionId?: string,
      claims?: Record<string, unknown>,
      tags?: Record<string, unknown>
    ) => {
      await auditService.logChatEvent(method, path, sessionId, claims, tags);
    },
    []
  );

  const logAPIRequest = useCallback(
    async (
      method: string,
      path: string,
      statusCode: number,
      inputBytes: number,
      outputBytes: number,
      timeToResponse: string,
      sessionId?: string,
      headers?: Record<string, string>
    ) => {
      await auditService.logAPIRequest(
        method,
        path,
        statusCode,
        inputBytes,
        outputBytes,
        timeToResponse,
        sessionId,
        headers
      );
    },
    []
  );

  const logError = useCallback(
    async (
      error: Error,
      method: string,
      path: string,
      sessionId?: string,
      tags?: Record<string, unknown>
    ) => {
      await auditService.logError(error, method, path, sessionId, tags);
    },
    []
  );

  return {
    logChatEvent,
    logAPIRequest,
    logError,
  };
}; 