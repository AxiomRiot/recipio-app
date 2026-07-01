import { Router } from 'express';

export const healthRouter = Router();

healthRouter.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'core-api', timestamp: new Date().toISOString() });
});
