import topicsJson from '../events/topics.json';

export const Topics = {
  SCRAPE_REQUESTED: 'scrape-requested',
  RECIPE_PARSED: 'recipe-parsed',
} as const;

export type TopicName = typeof Topics[keyof typeof Topics];
