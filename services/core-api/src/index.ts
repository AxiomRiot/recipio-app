import { app } from './app';
import { logger } from './logger';

const port = 1234;

logger.info('Starting Application');

app.listen(port, () => {
  logger.info(`Server is up on port ${port}`);
});
