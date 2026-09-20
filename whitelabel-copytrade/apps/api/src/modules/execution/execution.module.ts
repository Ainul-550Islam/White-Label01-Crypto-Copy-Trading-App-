import { Module } from '@nestjs/common';

import { ExchangeAccountsService } from './exchange-accounts.service';
import { ExecutionOrdersService } from './execution-orders.service';
import { ReconciliationService } from './reconciliation.service';
import { ExecutionIncidentsService } from './execution-incidents.service';
import { ExecutionSafetyService } from './execution-safety.service';
import { ExecutionCommandsService } from './execution-commands.service';
import { ExchangeAccountsController } from './exchange-accounts.controller';
import { ExecutionOrdersController } from './execution-orders.controller';
import { ExecutionAdminController } from './execution-admin.controller';

/**
 * Authenticated execution: the read and control surface over the money path.
 *
 * Not `@Global()`, unlike several Part 1 modules. Nothing else in the API
 * should be reaching into execution state, and a global module invites exactly
 * that. If another module ever needs one of these services, adding an explicit
 * import is the point at which someone asks whether it should.
 *
 * The module has no `exports` for the same reason.
 *
 * Note also what this module does not provide: no adapter, no signer, no
 * credential provider, no risk engine. Those live in the trading worker. This
 * module reads what the worker recorded and tells it what an operator wants
 * done; it cannot itself talk to a venue.
 */
@Module({
  controllers: [ExchangeAccountsController, ExecutionOrdersController, ExecutionAdminController],
  providers: [
    ExchangeAccountsService,
    ExecutionOrdersService,
    ReconciliationService,
    ExecutionIncidentsService,
    ExecutionSafetyService,
    ExecutionCommandsService,
  ],
})
export class ExecutionModule {}
