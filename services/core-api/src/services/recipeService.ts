import type { RecipeParsedEvent, ScrapeRequestEvent } from '@recipe-app/types-ts/events';
import type { EventProducer } from '../kafka/producer';
import { logger } from '../logger';

export class RecipeService {
  private producer: EventProducer;

  constructor(producer: EventProducer) {
    this.producer = producer;
  }

  public testEvent() {
    logger.info('Service called correctly');
  }

  public async sendScrapeRequest(url: string) {
    const date = new Date();

    logger.info(`Publishing scrape request event for URL: ${url}`);
    const event: ScrapeRequestEvent = {
      header: {
        event_id: crypto.randomUUID(),
        timestamp: date.toISOString(),
      },
      event_type: 'scrape-requested',
      url,
    };

    await this.producer.sendEvent('scrape-requested', event);
  }

  public async handleRecipeParsedEvent(event: RecipeParsedEvent): Promise<void> {
    logger.info(event);
  }
}
