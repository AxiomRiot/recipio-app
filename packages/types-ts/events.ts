import type { z } from 'zod';
import { RecipeParsedEventSchema, ScrapeRequestedEventSchema } from './schema';
import { Topics } from './topics';

// Type resolution
export type ScrapeRequestEvent = z.infer<typeof ScrapeRequestedEventSchema>;
export type RecipeParsedEvent = z.infer<typeof RecipeParsedEventSchema>;

// Topic mapping
export const EventSchemasByTopic = {
  [Topics.RECIPE_PARSED]: RecipeParsedEventSchema,
  [Topics.SCRAPE_REQUESTED]: ScrapeRequestedEventSchema,
} as const;

// derive the payload type for each topic directly from its Zod schema
export type EventPayloadMap = {
  [K in keyof typeof EventSchemasByTopic]: z.infer<typeof EventSchemasByTopic[K]>
};
