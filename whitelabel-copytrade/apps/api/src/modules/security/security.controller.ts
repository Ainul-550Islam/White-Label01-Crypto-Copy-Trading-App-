import { Body, Controller, Get, HttpCode, HttpStatus, Param, Post, Query } from '@nestjs/common';
import { ApiOkResponse, ApiOperation, ApiTags } from '@nestjs/swagger';
import { Permission, type PaginatedResult } from '@wlct/shared-types';
import type { AuthenticatedActor } from '@wlct/shared-types';

import { SecurityEventsService } from './security-events.service';
import { ListSecurityEventsDto } from './dto/list-security-events.dto';
import { ResolveSecurityEventDto } from './dto/resolve-security-event.dto';
import { CurrentUser } from '../../common/decorators/current-user.decorator';
import { TenantId } from '../../common/decorators/current-tenant.decorator';
import { RequirePermissions } from '../../common/decorators/permissions.decorator';
import { ApiStandardResponses } from '../../common/decorators/api-standard-responses.decorator';
import { ParseUuidPipe } from '../../common/pipes/parse-uuid.pipe';

@ApiTags('Security')
@Controller({ path: 'security/events', version: '1' })
@ApiStandardResponses()
export class SecurityController {
  constructor(private readonly securityEvents: SecurityEventsService) {}

  @Get()
  @HttpCode(HttpStatus.OK)
  @RequirePermissions(Permission.SECURITY_EVENT_READ)
  @ApiOperation({ summary: 'List security events for the current organisation' })
  @ApiOkResponse({ description: 'Paginated security events.' })
  async list(
    @Query() query: ListSecurityEventsDto,
    @TenantId() tenantId: string,
  ): Promise<PaginatedResult<unknown>> {
    return this.securityEvents.list({ ...query, tenantId });
  }

  @Post(':id/resolve')
  @HttpCode(HttpStatus.OK)
  @RequirePermissions(Permission.SECURITY_EVENT_READ)
  @ApiOperation({ summary: 'Mark a security event as reviewed and resolved' })
  @ApiOkResponse({ description: 'The event was marked resolved.' })
  async resolve(
    @Param('id', ParseUuidPipe) id: string,
    @Body() body: ResolveSecurityEventDto,
    @TenantId() tenantId: string,
    @CurrentUser() actor: AuthenticatedActor,
  ): Promise<{ id: string; resolved: true }> {
    await this.securityEvents.resolve(tenantId, id, actor.userId, body.resolution);
    return { id, resolved: true };
  }
}
