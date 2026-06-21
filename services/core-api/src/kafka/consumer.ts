// consumer.ts
import type { Consumer } from 'kafkajs';
import type { EventPayloadMap } from '../../../../packages/types/events';
import type { TopicName } from '../../../../packages/types/topics';
import { Kafka } from 'kafkajs';
import { EventSchemasByTopic } from '../../../../packages/types/events';

export type MessageHandler<T extends keyof EventPayloadMap = keyof EventPayloadMap> = (
  topic: T,
  event: EventPayloadMap[T],
  raw: { key: string | null },
) => Promise<void>;

export class EventConsumer {
  private mConsumer: Consumer;
  private mConnected = false;

  constructor(groupId: string) {
    const kafka = new Kafka({
      brokers: ['localhost:9092'],
    });

    this.mConsumer = kafka.consumer({ groupId });
  }

  public async connect() {
    if (this.mConnected)
      return;
    await this.mConsumer.connect();
    this.mConnected = true;
  }

  public async subscribe<T extends TopicName>(topics: T[], handler: MessageHandler): Promise<void> {
    if (!this.mConnected)
      throw new Error('[EventConsumer] Consumer not connected — call connect() first');

    await this.mConsumer.connect();
    await this.mConsumer.subscribe({ topics });

    await this.mConsumer.run({
      eachMessage: async ({ topic, message }) => {
        const key = message.key?.toString() ?? null;

        let raw: unknown;
        try {
          raw = JSON.parse(message.value!.toString());
        }
        catch (err) {
          console.error(`[EventConsumer] Failed to parse message on ${topic}`, err);
          return;
        }

        const schema = EventSchemasByTopic[topic as TopicName];
        const result = schema.safeParse(raw);

        if (!result.success) {
          console.error(`[EventConsumer] Schema validation failed on ${topic}`, result.error);
          return;
        }

        try {
          await handler(topic as T, result.data as EventPayloadMap[T], { key });
        }
        catch (err) {
          console.error(`[EventConsumer] Handler failed for ${topic}`, err);
          throw err;
        }
      },
    });
  }

  public async disconnect() {
    await this.mConsumer.disconnect();
    this.mConnected = false;
  }
}
