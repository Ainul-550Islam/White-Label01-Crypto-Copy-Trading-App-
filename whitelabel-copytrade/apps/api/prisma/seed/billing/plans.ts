/**
 * Plans Seed Data
 * 
 * This file contains seed data for billing plans.
 */

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function seedPlans() {
  console.log('Seeding plans...');

  const plans = [
    {
      id: 'plan-free',
      tenantId: 'system',
      name: 'Free',
      slug: 'free',
      description: 'Get started with basic trading features',
      tier: 'free',
      status: 'active',
      priceAmount: 0,
      priceCurrency: 'USD',
      priceInterval: 'monthly',
      trialDays: null,
      metadata: {},
    },
    {
      id: 'plan-basic',
      tenantId: 'system',
      name: 'Basic',
      slug: 'basic',
      description: 'Perfect for individual traders getting started',
      tier: 'basic',
      status: 'active',
      priceAmount: 29,
      priceCurrency: 'USD',
      priceInterval: 'monthly',
      trialDays: 7,
      metadata: {},
    },
    {
      id: 'plan-standard',
      tenantId: 'system',
      name: 'Standard',
      slug: 'standard',
      description: 'For serious traders who need more power',
      tier: 'standard',
      status: 'active',
      priceAmount: 79,
      priceCurrency: 'USD',
      priceInterval: 'monthly',
      trialDays: 14,
      metadata: {},
    },
    {
      id: 'plan-premium',
      tenantId: 'system',
      name: 'Premium',
      slug: 'premium',
      description: 'Full access to all features for professional traders',
      tier: 'premium',
      status: 'active',
      priceAmount: 199,
      priceCurrency: 'USD',
      priceInterval: 'monthly',
      trialDays: 30,
      metadata: {},
    },
    {
      id: 'plan-enterprise',
      tenantId: 'system',
      name: 'Enterprise',
      slug: 'enterprise',
      description: 'Custom solutions for large organizations',
      tier: 'enterprise',
      status: 'active',
      priceAmount: 0,
      priceCurrency: 'USD',
      priceInterval: 'monthly',
      trialDays: null,
      metadata: { custom: 'true' },
    },
  ];

  for (const plan of plans) {
    await prisma.plan.upsert({
      where: { id: plan.id },
      update: plan,
      create: plan,
    });
  }

  console.log(`Seeded ${plans.length} plans`);
}