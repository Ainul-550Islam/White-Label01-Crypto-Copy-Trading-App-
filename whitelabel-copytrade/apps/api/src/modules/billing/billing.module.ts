import { Module } from '@nestjs/common';

import { PlansService } from './plans.service';
import { SubscriptionsService } from './subscriptions.service';
import { PlansController } from './plans.controller';
import { SubscriptionsController } from './subscriptions.controller';

/**
 * Subscription management.
 *
 * Part 1 owns the plan catalogue, tenant subscription lifecycle and the
 * entitlement checks that other modules rely on. Payment capture is delegated
 * to an external provider behind `BILLING_PROVIDER`; the provider adapters and
 * webhook ingestion land with the commercial work in a later part, which is why
 * no card data or provider secret ever touches this codebase.
 */
@Module({
  controllers: [PlansController, SubscriptionsController],
  providers: [PlansService, SubscriptionsService],
  exports: [PlansService, SubscriptionsService],
})
export class BillingModule {}
