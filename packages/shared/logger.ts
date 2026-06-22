import winston from 'winston';

const { combine, timestamp, printf } = winston.format;

export const logger = winston.createLogger({
  level: 'info',
  format: combine(
    winston.format.colorize(),
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    printf(info => `${info.timestamp} ${info.level}: ${info.message}`),
  ),
});

logger.add(new winston.transports.Console());
