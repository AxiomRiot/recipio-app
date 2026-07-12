import { object, z } from 'zod';

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
    site_name: z.string(),
    description: z.string(),
    category: z.string(),
    cuisine: z.string(),
    image_url: z.string(),
    servings: z.string(),
    nutrients: z.record(z.string(), z.string()),
    prep_time_min: z.number().gt(0),
    cook_time_min: z.number().gt(0),
    ratings: z.number().lte(5).gt(0),
    ratings_count: z.number(),
    steps: z.array(z.string()),
    ingredients: z.array(z.object({
      name: z.string(),
      quantity: z.number(),
      unit: z.string().optional(),
    })),
  }),
});
