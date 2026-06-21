import type { Router } from 'express';
import type { RecipeController } from '../controllers/recipeController';
import express from 'express';

export class RecipeRouter {
  private router: Router;

  constructor(private controller: RecipeController) {
    this.router = express.Router();

    this.router.post('/recipe', controller.sendScrapeRequest);
  }

  public getRouter(): Router {
    return this.router;
  }
}
