import type { RecipeParsedEvent, ScrapeRequestEvent } from '@recipe-app/types/events';
import type { EventProducer } from '../kafka/producer';
import { logger } from '../logger';

export class RecipeService {
  private producer: EventProducer;

  constructor(producer: EventProducer) {
    this.producer = producer;
  }

  public async sendScrapeRequest(url: string) {
    logger.info(`Publishing scrape request event for URL: ${url}`);
    const event: ScrapeRequestEvent = {
      header: {
        event_id: crypto.randomUUID(),
        timestamp: Date.now().toLocaleString(),
      },
      event_type: 'scrape-requested',
      url,
    };

    this.producer.sendEvent('scrape-requested', event);
  }

  public async handleRecipeParsedEvent(event: RecipeParsedEvent): Promise<void> {
    await console.warn(event);
  }
}
