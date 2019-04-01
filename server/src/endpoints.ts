import * as express from 'express';
import * as bodyParser from 'body-parser';

let app = express();

app.use(bodyParser.json());

app.get('/new', function(req, res) {
  console.log('Starting new DML Session...');
  res.end("Starting new DML Session...");



  // 1. Mark the service as BUSY.

  // 2. Decode new message from Explora with:
  //    - Metadata (user, repo, logging info)
  //    - Model + weights + optimizer (h5 binary format)
  //    - Hyperparameters
  //    - Selection Criteria

  // 3.
});

export { app };
