import * as express from 'express';
import * as bodyParser from 'body-parser';

let app = express();

app.use(bodyParser.json());

app.get('/new', function(req, res) {
  console.log('Starting new DML Session...');
  res.end("Starting new DML Session...");

  // 1. If server is BUSY, error. Otherwise, mark the service as BUSY.

  // 2. Set the internal round variable to 1, reset the number of nodes
  //    averaged to 0.

  // 3. Decode new message from Explora with:
  //    - Metadata (user, repo, logging info)
  //    - Model + weights + optimizer (in .h5 binary format)
  //    - Hyperparameters (batch size, learning rate, decay)
  //    - Selection Criteria (i.e., nodes with more than 1000 data points)
  //    - Continuation Criteria (i.e., 80% of selected nodes weights averaged)
  //    - Termination Criteria (i.e., 20 FL rounds completed)

  // 4. Decode the weights and store them in memory.
  //    (Will be used for running weighted average.)

  // 5. According to the 'Selection Criteria', choose clients to forward
  //    training messages to and kickstart a DML Session with round # 1
});

// TODO: Put a loop somewhere to support timing out. For example, if the service
// hasn't received a message for more than 15 minutes, it resets all connections,
// and resumes training from the last weights it has access to. It should retry
// this 3 or so times.

export { app };
