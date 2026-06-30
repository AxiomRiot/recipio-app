import process from 'node:process';
import winston from 'winston';

const { combine, timestamp, printf } = winston.format;

export function createServiceLogger(serviceName: string): winston.Logger {
  const loggerFormat = printf(({ timestamp: ts, level, message, stack, ...meta }) => {
    const extra = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';
    const error = stack ? `\n${stack}` : '';

    return `${ts} ${level}: ${message}${extra}${error}`;
  });

  const logger = winston.createLogger({
    level: process.env.LOG_LEVEL ?? 'info',
    defaultMeta: serviceName,
    format: combine(
      winston.format.colorize(),
      timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      loggerFormat,
    ),
    transports: [
      new winston.transports.Console(),
    ],
  });

  return logger;
}