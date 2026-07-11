import { z } from 'zod';

/**
 * Event header found in every schema
 */
const EventHeaderSchema = z.object({
  event_id: z.uuid(),
  timestamp: z.string(),
});

/**
 * Request for scraping a site
 */
export const ScrapeRequestedEventSchema = z.object({
  header: EventHeaderSchema,
  event_type: z.literal('scrape-requested'),
  url: z.string(),
});

/**
 * Recipe parsed schema, contains recipe payload. Response to the scrape request
 */
export const RecipeParsedEventSchema = z.object({
  header: EventHeaderSchema,
  event_type: z.literal('recipe-parsed'),
  payload: z.object({
    title: z.string(),
    url: z.string(),
    description: z.string(),
    servings: z.string(),
    duration: z.object({
      days: z.number().int().positive(),
      hours: z.number().int().lt(24),
      minutes: z.number().int().positive().lt(60),
    }),
    steps: z.array(z.string()),
    ingredients: z.array(z.object({
      name: z.string(),
      quantity: z.number(),
      unit: z.string().optional(),
    })),
  }),
});
