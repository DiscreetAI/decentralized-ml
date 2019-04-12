import { LayersModel, Tensor, Rank } from '@tensorflow/tfjs';
import { loadLayersModel } from '@tensorflow/tfjs';
//import * as tfvis from '@tensorflow/tfjs-vis';

class MLModule {
    private async getModel() {
        const MODEL_URL = 'http://localhost:5000/server/model.json';
        const model: LayersModel = await loadLayersModel(MODEL_URL);
        console.log("Model loaded!", model);
        return model;
      }

    async trainModel(batch_size:number, epochs:number, shuffle: boolean,
        trainXs:Tensor, trainYs:Tensor) {
        // const metrics = ['loss', 'acc'];
      
        //const BATCH_SIZE = 128;
        //const TRAIN_DATA_SIZE = 8000;
      
        // const [trainXs, trainYs] = tf.tidy(() => {
        //   const d = data.nextTrainBatch(train_data_size);
        //   return [
        //     d.xs.reshape([train_data_size, 784]),
        //     d.labels.argMax([-1])
        //   ];
        // });
        const model: LayersModel = await this.getModel();
        return model.fit(trainXs, trainYs, {
          batchSize: batch_size,
          epochs: epochs,
          shuffle: shuffle,
        });
      }

      async evaluateModel(testxs:Tensor, testys:Tensor) {
        // const IMAGE_WIDTH = 28;
        // const IMAGE_HEIGHT = 28;
        // const TEST_DATA_SIZE = data.testIndices.length;
        // //const TEST_DATA_SIZE = 100;
        // const testData = data.nextTestBatch(TEST_DATA_SIZE);
        // const testxs = testData.xs.reshape([TEST_DATA_SIZE, IMAGE_WIDTH * IMAGE_HEIGHT]);
        // const labels = testData.labels.argMax([-1]);
        const model: LayersModel = await this.getModel();
        return model.evaluate(testxs, testys);
      
        // testxs.dispose();
      
        // console.log("Model evaluated!");
        // // return [labels, preds];
        // return results;
      }
}