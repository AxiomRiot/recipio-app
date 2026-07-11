import type { EventPayloadMap } from '@recipe-app/types-ts/events';
import type { Producer } from 'kafkajs';
import { Kafka } from 'kafkajs';

export class EventProducer {
  private mProducer: Producer;
  private mConnected = false;

  constructor(brokerAddr: string) {
    const kafka = new Kafka({
      clientId: 'core-api-service',
      brokers: [brokerAddr],
    });

    this.mProducer = kafka.producer();
  }

  public async connect() {
    if (this.mConnected)
      return;
    await this.mProducer.connect();
    this.mConnected = true;
  }

  public async sendEvent<T extends keyof EventPayloadMap = keyof EventPayloadMap>(topic: T, event: EventPayloadMap[T]) {
    if (!this.mConnected)
      await this.connect();

    await this.mProducer.send({
      topic,
      messages: [
        {
          key: event.header.event_id,
          value: JSON.stringify(event),
        },
      ],
    });
  }

  public async disconnect() {
    await this.mProducer.disconnect();
    this.mConnected = false;
  }
}
