import type { Request, Response } from 'express';
import type { RecipeService } from '../services/recipeService';
import { logger } from '../logger';

export class RecipeController {
  constructor(private service: RecipeService) {}

  public async sendScrapeRequest(req: Request, res: Response) {
    const url = req.body.url;
    logger.info(`Controller received scrape request for url: ${url}`);

    if (!url) {
      return res.status(400).send('Recipe URL is required');
    }

    try {
      await this.service.sendScrapeRequest(url);
      res.status(201).send();
    }
    catch (error) {
      res.status(500).send(`Error creating recipe: ${error}`);
    }
  }
}
