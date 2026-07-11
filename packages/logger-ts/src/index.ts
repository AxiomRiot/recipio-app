import process from 'node:process';
import winston from 'winston';

const { combine, timestamp, json } = winston.format;

export function createServiceLogger(serviceName: string): winston.Logger {
  const logger = winston.createLogger({
    level: process.env.LOG_LEVEL ?? 'info',
    defaultMeta: { service: serviceName },
    format: combine(
      timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      json(),
    ),
    transports: [
      new winston.transports.Console(),
    ],
  });

  return logger;
}
