import type { Router } from 'express';
import type { RecipeController } from '../controllers/recipeController';
import express from 'express';

export class RecipeRouter {
  private router: Router;
  private controller: RecipeController;

  constructor(private control: RecipeController) {
    this.router = express.Router();
    this.controller = control;

    // Bind the controller method so `this` refers to the controller instance
    this.router.post('/recipe', this.controller.sendScrapeRequest.bind(this.controller));
  }

  public getRouter(): Router {
    return this.router;
  }
}
