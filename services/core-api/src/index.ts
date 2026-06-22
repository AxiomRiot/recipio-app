import { logger } from '../../../packages/shared/logger';
import { app } from './app';

const port = 8080;

logger.info('Starting Application');

app.listen(port, () => {
  logger.info(`Server is up on port ${port}`);
});
