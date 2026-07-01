import process from 'node:process';
import { Topics } from '@recipe-app/types/topics';
import express, { Router } from 'express';
import { RecipeController } from './controllers/recipeController';
import { EventConsumer } from './kafka/consumer';
import { EventProducer } from './kafka/producer';
import { healthRouter } from './routes/health';
import { RecipeRouter } from './routes/recipes';
import { RecipeService } from './services/recipeService';

const brokerAddress = process.env.KAFKA_BROKER || 'localhost:9092';
const groupId = process.env.KAFKA_GROUP_ID || 'core-api';

// Producers
const scrapRecipeEventProducer: EventProducer
  = new EventProducer(brokerAddress);

scrapRecipeEventProducer.connect();

// Services
const recipeService: RecipeService = new RecipeService(scrapRecipeEventProducer);

// Consumers
const recipeConsumer: EventConsumer = new EventConsumer(groupId);
recipeConsumer.connect();

recipeConsumer.subscribe([Topics.RECIPE_PARSED], async (topic, event) => {
  if (event.event_type !== Topics.RECIPE_PARSED) {
    return;
  }

  await recipeService.handleRecipeParsedEvent(event);
});

// Controllers
const recipeController: RecipeController = new RecipeController(recipeService);

// Routers
const recipeRouter: RecipeRouter = new RecipeRouter(recipeController);

export const app = express();

app.use(express.json());
app.use(recipeRouter.getRouter());
app.use(healthRouter);

process.on('SIGTERM', async () => {
  await recipeConsumer.disconnect();
  await scrapRecipeEventProducer.disconnect();
});
