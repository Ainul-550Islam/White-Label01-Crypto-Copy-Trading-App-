import { Global, Module } from '@nestjs/common';

import { SecurityEventsService } from './security-events.service';
import { SuspiciousLoginDetector } from './suspicious-login.detector';
import { SecurityController } from './security.controller';

/**
 * Security telemetry: detection, recording and review of anomalous behaviour.
 * Global so authentication and tenancy guards can emit events directly.
 */
@Global()
@Module({
  controllers: [SecurityController],
  providers: [SecurityEventsService, SuspiciousLoginDetector],
  exports: [SecurityEventsService, SuspiciousLoginDetector],
})
export class SecurityModule {}
