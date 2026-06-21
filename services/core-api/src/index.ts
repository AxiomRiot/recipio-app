import { app } from './app';

const port = 8080;

console.info('Starting Application');

app.listen(port, () => {
  console.info(`Server is up on port ${port}`);
});
